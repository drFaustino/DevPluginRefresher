import os
import inspect

from qgis.PyQt.QtCore import (
    QSettings, QFileSystemWatcher, QCoreApplication, Qt
)
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsMessageLog, Qgis
from qgis.utils import reloadPlugin, plugins

from .refresher_dock import RefresherDock

class DevPluginRefresher:
    def __init__(self, iface):
        self.iface = iface
        self.dock = None
        self.action_open = None

        self.watcher = QFileSystemWatcher()
        self.target_plugin = None
        self.settings_key = "DevPluginRefresher/target_plugin"

        self.watcher.fileChanged.connect(self._on_file_changed)
        self.watcher.directoryChanged.connect(self._on_dir_changed)

    # ----------------- QGIS lifecycle -----------------

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.action_open = QAction(
            QIcon(icon_path), "Open DevPluginRefresher", self.iface.mainWindow()
        )

        self.action_open.triggered.connect(self.open_dock)

        self.iface.addPluginToMenu("&DevPluginRefresher", self.action_open)
        self.iface.addToolBarIcon(self.action_open)

    def unload(self):
        self.iface.removePluginMenu("&DevPluginRefresher", self.action_open)
        self.iface.removeToolBarIcon(self.action_open)
        if self.dock:
            self.iface.removeDockWidget(self.dock)
        self._clear_watcher()

    # ----------------- UI -----------------

    def open_dock(self):
        if not self.dock:
            self.dock = RefresherDock(self.iface.mainWindow())
            self.iface.addDockWidget(
                Qt.DockWidgetArea.RightDockWidgetArea, self.dock
            )

            self._populate_plugin_list()

            self.dock.plugin_combo.currentTextChanged.connect(
                self._plugin_selected
            )
            self.dock.reload_btn.clicked.connect(self.reload_selected_plugin)
            self.dock.auto_reload.toggled.connect(self._toggle_auto_reload)
            self.dock.clear_btn.clicked.connect(self._clear_log)

        self.dock.show()

    def _populate_plugin_list(self):
        plugin_list = sorted(plugins.keys())  # only loaded plugins
        self.dock.plugin_combo.clear()
        self.dock.plugin_combo.addItems(plugin_list)

        # If no plugins loaded, nothing to do
        if not plugin_list:
            self._log("No loaded Python plugins found.")
            return

        # Load last plugin if exists
        last = self._load_last_plugin()

        if last in plugin_list:
            # Restore last selected plugin
            self.dock.plugin_combo.setCurrentText(last)
            self.target_plugin = last
            self._setup_watcher()
            self._log(f"Restored last plugin: {last}")
        else:
            # FIRST START → select first plugin automatically
            first = plugin_list[0]
            self.dock.plugin_combo.setCurrentText(first)
            self.target_plugin = first
            self._save_last_plugin()
            self._setup_watcher()
            self._log(f"Loaded first plugin automatically: {first}")

    # ----------------- Plugin selection -----------------

    def _plugin_selected(self, name: str):
        self.target_plugin = name if name else None
        self._save_last_plugin()
        self._setup_watcher()
        self._log(f"Selected plugin: {name}")

    # ----------------- Reload -----------------

    def reload_selected_plugin(self):
        if not self.target_plugin:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "No plugin",
                "Select a plugin first.",
            )
            return

        if self.target_plugin not in plugins:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Plugin not loaded",
                f"Plugin '{self.target_plugin}' is not loaded in this session.",
            )
            self._log(
                "Plugin '{self.target_plugin}' not found among loaded plugins.",
                Qgis.Warning,
            )
            return

        try:
            reloadPlugin(self.target_plugin)
            self._log(f"Plugin '{self.target_plugin}' reloaded successfully.")
        except Exception as e:
            self._log(f"Error reloading plugin '{self.target_plugin}': {e}",
                      Qgis.Critical)
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                f"Error reloading plugin '{self.target_plugin}':\n{e}",
            )

    # ----------------- Auto reload -----------------

    def _toggle_auto_reload(self, enabled: bool):
        if enabled:
            self._setup_watcher()
            self._log("Auto-reload enabled.")
        else:
            self._clear_watcher()
            self._log("Auto-reload disabled.")

    def _setup_watcher(self):
        self._clear_watcher()
        if not self.target_plugin:
            return
        if self.target_plugin not in plugins:
            return

        plugin_obj = plugins[self.target_plugin]

        # Try to get the file of the plugin class
        try:
            plugin_file = inspect.getfile(plugin_obj.__class__)
        except Exception:
            return

        plugin_dir = os.path.dirname(plugin_file)
        if not os.path.isdir(plugin_dir):
            return

        # Watch directory and .py files
        self.watcher.addPath(plugin_dir)
        for fname in os.listdir(plugin_dir):
            if fname.endswith(".py"):
                self.watcher.addPath(os.path.join(plugin_dir, fname))

        self._log(f"Watching directory: {plugin_dir}")

    def _clear_watcher(self):
        files = self.watcher.files()
        if files:
            self.watcher.removePaths(files)
        dirs = self.watcher.directories()
        if dirs:
            self.watcher.removePaths(dirs)

    def _on_file_changed(self, path: str):
        if not self.dock or not self.dock.auto_reload.isChecked():
            return
        if not path.endswith(".py"):
            return
        self._log(f"Detected .py change: {path}")
        self.reload_selected_plugin()

    def _on_dir_changed(self, path: str):
        if not self.dock or not self.dock.auto_reload.isChecked():
            return
        self._log(f"Directory changed: {path}")
        self.reload_selected_plugin()

    # ----------------- Settings -----------------

    def _load_last_plugin(self) -> str:
        s = QSettings()
        return s.value(self.settings_key, "", type=str)

    def _save_last_plugin(self):
        s = QSettings()
        s.setValue(self.settings_key, self.target_plugin)

    # ----------------- Logging -----------------

    def _log(self, msg: str, level=Qgis.Info):
        QgsMessageLog.logMessage(msg, "DevPluginRefresher", level)
        if self.dock:
            self.dock.log(msg)
    
    def _clear_log(self):
        if self.dock:
            self.dock.clear_log()

