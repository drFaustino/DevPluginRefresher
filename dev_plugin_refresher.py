import inspect
import os

from qgis.PyQt.QtCore import (
    QCoreApplication,
    QFileSystemWatcher,
    QSettings,
    QTimer,
    Qt,
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QAction,
    QMessageBox,
)
from qgis.core import (
    Qgis,
    QgsMessageLog,
)
from qgis.utils import (
    plugins,
    reloadPlugin,
)

from .refresher_dock import RefresherDock


class DevPluginRefresher:

    PLUGIN_NAME = "DevPluginRefresher"

    SETTINGS_PLUGIN = (
        "DevPluginRefresher/target_plugin"
    )

    SETTINGS_AUTO_RELOAD = (
        "DevPluginRefresher/auto_reload"
    )

    def __init__(self, iface):

        self.iface = iface

        self.dock = None
        self.action_open = None

        self.watcher = QFileSystemWatcher()

        self.target_plugin = None

        self.reload_pending = False

        self.reload_timer = QTimer()
        self.reload_timer.setSingleShot(True)
        self.reload_timer.setInterval(700)

        self.reload_timer.timeout.connect(
            self._perform_auto_reload
        )

        self.watcher.fileChanged.connect(
            self._on_file_changed
        )

        self.watcher.directoryChanged.connect(
            self._on_directory_changed
        )

    # =========================================================
    # TRANSLATION
    # =========================================================

    @staticmethod
    def tr(message):

        return QCoreApplication.translate(
            "DevPluginRefresher",
            message
        )

    # =========================================================
    # GUI
    # =========================================================

    def initGui(self):

        icon_path = os.path.join(
            os.path.dirname(__file__),
            "icon.png"
        )

        self.action_open = QAction(
            QIcon(icon_path),
            self.tr(
                "Open DevPluginRefresher"
            ),
            self.iface.mainWindow()
        )

        self.action_open.triggered.connect(
            self.open_dock
        )

        self.iface.addPluginToMenu(
            "&DevPluginRefresher",
            self.action_open
        )

        self.iface.addToolBarIcon(
            self.action_open
        )

    def unload(self):

        self.reload_timer.stop()

        self._clear_watcher()

        if self.action_open:

            self.iface.removePluginMenu(
                "&DevPluginRefresher",
                self.action_open
            )

            self.iface.removeToolBarIcon(
                self.action_open
            )

            self.action_open.deleteLater()
            self.action_open = None

        if self.dock:

            self.iface.removeDockWidget(
                self.dock
            )

            self.dock.deleteLater()
            self.dock = None

    # =========================================================
    # DOCK
    # =========================================================

    def open_dock(self):

        if self.dock is None:

            self.dock = RefresherDock(
                self.iface.mainWindow()
            )

            self.iface.addDockWidget(
                Qt.DockWidgetArea.RightDockWidgetArea,
                self.dock
            )

            self.dock.plugin_combo.currentTextChanged.connect(
                self._plugin_selected
            )

            self.dock.reload_btn.clicked.connect(
                self.reload_selected_plugin
            )

            self.dock.auto_reload.toggled.connect(
                self._toggle_auto_reload
            )

            self.dock.clear_btn.clicked.connect(
                self._clear_log
            )

            self._populate_plugin_list()

            self._restore_auto_reload()

        self.dock.show()
        self.dock.raise_()

    # =========================================================
    # PLUGIN LIST
    # =========================================================

    def _populate_plugin_list(self):

        if self.dock is None:
            return

        plugin_list = sorted(
            plugins.keys()
        )

        self.dock.plugin_combo.blockSignals(
            True
        )

        self.dock.plugin_combo.clear()

        self.dock.plugin_combo.addItems(
            plugin_list
        )

        self.dock.plugin_combo.blockSignals(
            False
        )

        if not plugin_list:

            self._log(
                self.tr(
                    "No loaded Python plugins found."
                ),
                Qgis.Warning
            )

            return

        last_plugin = (
            self._load_last_plugin()
        )

        if last_plugin in plugin_list:

            self.target_plugin = last_plugin

        else:

            self.target_plugin = plugin_list[0]

            self._save_last_plugin()

        self.dock.plugin_combo.blockSignals(
            True
        )

        self.dock.plugin_combo.setCurrentText(
            self.target_plugin
        )

        self.dock.plugin_combo.blockSignals(
            False
        )

        self._log(
            self.tr(
                "Selected plugin: {0}"
            ).format(
                self.target_plugin
            )
        )

    def _plugin_selected(self, name):

        if not name:

            self.target_plugin = None

            self._clear_watcher()

            return

        self.target_plugin = name

        self._save_last_plugin()

        self._log(
            self.tr(
                "Selected plugin: {0}"
            ).format(name)
        )

        if (
            self.dock
            and self.dock.auto_reload.isChecked()
        ):

            self._setup_watcher()

    # =========================================================
    # MANUAL RELOAD
    # =========================================================

    def reload_selected_plugin(self):

        if not self.target_plugin:

            QMessageBox.warning(
                self.iface.mainWindow(),
                self.tr("No plugin"),
                self.tr(
                    "Select a plugin first."
                )
            )

            return

        plugin_name = self.target_plugin

        if plugin_name not in plugins:

            QMessageBox.warning(
                self.iface.mainWindow(),
                self.tr("Plugin not loaded"),
                self.tr(
                    "Plugin '{0}' is not loaded."
                ).format(
                    plugin_name
                )
            )

            return

        # IMPORTANT:
        # Save the state BEFORE reloadPlugin().
        auto_reload = False

        if self.dock is not None:

            try:
                auto_reload = (
                    self.dock.auto_reload.isChecked()
                )
            except RuntimeError:
                auto_reload = False

        self._save_state(
            plugin_name,
            auto_reload
        )

        # -----------------------------------------------------
        # SPECIAL CASE: reload ourselves
        # -----------------------------------------------------

        if (
            plugin_name
            == self.PLUGIN_NAME
        ):

            self._reload_self(
                auto_reload
            )

            return

        # -----------------------------------------------------
        # Normal plugin reload
        # -----------------------------------------------------

        try:

            self._clear_watcher()

            self._log(
                self.tr(
                    "Reloading plugin '{0}'..."
                ).format(
                    plugin_name
                )
            )

            reloadPlugin(
                plugin_name
            )

            self._log(
                self.tr(
                    "Plugin '{0}' reloaded successfully."
                ).format(
                    plugin_name
                )
            )

            # self.dock may still exist,
            # but check it before using it.
            if (
                auto_reload
                and self.dock is not None
            ):

                self._setup_watcher()

        except Exception as error:

            self._show_reload_error(
                plugin_name,
                error
            )

    # =========================================================
    # RELOAD OURSELVES
    # =========================================================

    def _reload_self(
        self,
        auto_reload
    ):

        self._log(
            self.tr(
                "Reloading DevPluginRefresher..."
            )
        )

        # Save everything before unloading.
        self._save_state(
            self.target_plugin,
            auto_reload
        )

        self._clear_watcher()

        # The current Qt event must finish
        # before QGIS unloads/reloads us.
        QTimer.singleShot(
            150,
            self._perform_self_reload
        )

    def _perform_self_reload(self):

        try:

            reloadPlugin(
                self.PLUGIN_NAME
            )

        except Exception as error:

            QgsMessageLog.logMessage(
                self.tr(
                    "Error reloading DevPluginRefresher: {0}"
                ).format(error),
                self.PLUGIN_NAME,
                Qgis.Critical
            )

            QMessageBox.critical(
                self.iface.mainWindow(),
                self.tr("Reload error"),
                self.tr(
                    "Error reloading DevPluginRefresher:\n{0}"
                ).format(error)
            )

            return

        # Get the NEW instance.
        new_plugin = plugins.get(
            self.PLUGIN_NAME
        )

        if new_plugin is None:

            QMessageBox.critical(
                self.iface.mainWindow(),
                self.tr("Reload error"),
                self.tr(
                    "DevPluginRefresher could not be reloaded."
                )
            )

            return

        # Open a new dock.
        new_plugin.open_dock()

        if new_plugin.dock is None:
            return

        # Restore selected plugin.
        selected_plugin = (
            new_plugin._load_last_plugin()
        )

        if (
            selected_plugin
            and selected_plugin in plugins
        ):

            new_plugin.target_plugin = (
                selected_plugin
            )

            new_plugin.dock.plugin_combo.blockSignals(
                True
            )

            new_plugin.dock.plugin_combo.setCurrentText(
                selected_plugin
            )

            new_plugin.dock.plugin_combo.blockSignals(
                False
            )

        # Restore auto reload.
        auto_reload = QSettings().value(
            new_plugin.SETTINGS_AUTO_RELOAD,
            False,
            type=bool
        )

        new_plugin.dock.auto_reload.blockSignals(
            True
        )

        new_plugin.dock.auto_reload.setChecked(
            auto_reload
        )

        new_plugin.dock.auto_reload.blockSignals(
            False
        )

        if auto_reload:

            new_plugin._setup_watcher()

        new_plugin._log(
            new_plugin.tr(
                "DevPluginRefresher reloaded successfully."
            )
        )

    # =========================================================
    # AUTO RELOAD
    # =========================================================

    def _toggle_auto_reload(
        self,
        enabled
    ):

        QSettings().setValue(
            self.SETTINGS_AUTO_RELOAD,
            enabled
        )

        if enabled:

            self._setup_watcher()

            self._log(
                self.tr(
                    "Auto-reload enabled."
                )
            )

        else:

            self.reload_timer.stop()

            self._clear_watcher()

            self._log(
                self.tr(
                    "Auto-reload disabled."
                )
            )

    def _setup_watcher(self):

        self._clear_watcher()

        if not self.target_plugin:
            return

        if (
            self.target_plugin
            not in plugins
        ):
            return

        # Never automatically reload ourselves.
        if (
            self.target_plugin
            == self.PLUGIN_NAME
        ):

            self._log(
                self.tr(
                    "DevPluginRefresher is not watched by auto-reload."
                )
            )

            return

        plugin_object = plugins[
            self.target_plugin
        ]

        try:

            plugin_file = inspect.getfile(
                plugin_object.__class__
            )

        except Exception as error:

            self._log(
                self.tr(
                    "Cannot find plugin file: {0}"
                ).format(error),
                Qgis.Warning
            )

            return

        plugin_dir = os.path.dirname(
            plugin_file
        )

        if not os.path.isdir(
            plugin_dir
        ):

            return

        # Watch directory.
        self.watcher.addPath(
            plugin_dir
        )

        # Watch Python files.
        for filename in os.listdir(
            plugin_dir
        ):

            if filename.endswith(
                ".py"
            ):

                filepath = os.path.join(
                    plugin_dir,
                    filename
                )

                self.watcher.addPath(
                    filepath
                )

        self._log(
            self.tr(
                "Watching: {0}"
            ).format(
                plugin_dir
            )
        )

    # =========================================================
    # WATCHER
    # =========================================================

    def _on_file_changed(
        self,
        path
    ):

        if not self._auto_reload_active():
            return

        if not path.endswith(
            ".py"
        ):
            return

        self._log(
            self.tr(
                "Python file changed: {0}"
            ).format(path)
        )

        self._schedule_auto_reload()

    def _on_directory_changed(
        self,
        path
    ):

        if not self._auto_reload_active():
            return

        self._log(
            self.tr(
                "Plugin directory changed: {0}"
            ).format(path)
        )

        self._schedule_auto_reload()

    def _auto_reload_active(self):

        if self.dock is None:
            return False

        try:

            return (
                self.dock.auto_reload.isChecked()
            )

        except RuntimeError:

            return False

    def _schedule_auto_reload(self):

        self.reload_pending = True

        self.reload_timer.start()

    def _perform_auto_reload(self):

        if not self.reload_pending:
            return

        self.reload_pending = False

        if not self._auto_reload_active():
            return

        self.reload_selected_plugin()

    # =========================================================
    # WATCHER CLEANUP
    # =========================================================

    def _clear_watcher(self):

        files = self.watcher.files()

        if files:

            self.watcher.removePaths(
                files
            )

        directories = (
            self.watcher.directories()
        )

        if directories:

            self.watcher.removePaths(
                directories
            )

    # =========================================================
    # SETTINGS
    # =========================================================

    def _load_last_plugin(self):

        return QSettings().value(
            self.SETTINGS_PLUGIN,
            "",
            type=str
        )

    def _save_last_plugin(self):

        QSettings().setValue(
            self.SETTINGS_PLUGIN,
            self.target_plugin
        )

    def _save_state(
        self,
        plugin_name,
        auto_reload
    ):

        settings = QSettings()

        if plugin_name:
            settings.setValue(
                self.SETTINGS_PLUGIN,
                plugin_name
            )

        settings.setValue(
            self.SETTINGS_AUTO_RELOAD,
            auto_reload
        )

    def _restore_auto_reload(self):

        if self.dock is None:
            return

        enabled = QSettings().value(
            self.SETTINGS_AUTO_RELOAD,
            False,
            type=bool
        )

        self.dock.auto_reload.blockSignals(
            True
        )

        self.dock.auto_reload.setChecked(
            enabled
        )

        self.dock.auto_reload.blockSignals(
            False
        )

        if enabled:

            self._setup_watcher()

    # =========================================================
    # LOG
    # =========================================================

    def _log(
        self,
        message,
        level=Qgis.Info
    ):

        QgsMessageLog.logMessage(
            str(message),
            self.PLUGIN_NAME,
            level
        )

        if self.dock:

            try:

                self.dock.log(
                    str(message)
                )

            except RuntimeError:

                self.dock = None

    def _clear_log(self):

        if self.dock:

            try:

                self.dock.clear_log()

            except RuntimeError:

                self.dock = None

    # =========================================================
    # ERROR
    # =========================================================

    def _show_reload_error(
        self,
        plugin_name,
        error
    ):

        message = self.tr(
            "Error reloading '{0}': {1}"
        ).format(
            plugin_name,
            error
        )

        self._log(
            message,
            Qgis.Critical
        )

        QMessageBox.critical(
            self.iface.mainWindow(),
            self.tr("Reload error"),
            self.tr(
                "Error reloading '{0}':\n{1}"
            ).format(
                plugin_name,
                error
            )
        )
