import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class RefresherDock(QDockWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(parent)

        self.setWindowTitle(
            self.tr(
                "DevPluginRefresher"
            )
        )

        self.setMinimumWidth(
            380
        )

        self.setMinimumHeight(
            420
        )

        icon_path = os.path.join(
            os.path.dirname(__file__),
            "icon.png"
        )

        if os.path.exists(
            icon_path
        ):

            self.setWindowIcon(
                QIcon(icon_path)
            )

        container = QWidget()

        layout = QVBoxLayout(
            container
        )

        # -----------------------------------------------------
        # Plugin selector
        # -----------------------------------------------------

        self.plugin_label = QLabel(
            self.tr(
                "Select plugin:"
            )
        )

        layout.addWidget(
            self.plugin_label
        )

        self.plugin_combo = QComboBox()

        layout.addWidget(
            self.plugin_combo
        )

        # -----------------------------------------------------
        # Auto reload
        # -----------------------------------------------------

        self.auto_reload = QCheckBox(
            self.tr(
                "Auto-reload when .py files change"
            )
        )

        layout.addWidget(
            self.auto_reload
        )

        # -----------------------------------------------------
        # Buttons
        # -----------------------------------------------------

        btn_layout = QHBoxLayout()

        self.reload_btn = QPushButton(
            self.tr(
                "Reload now"
            )
        )

        self.clear_btn = QPushButton(
            self.tr(
                "Clear log"
            )
        )

        btn_layout.addWidget(
            self.reload_btn
        )

        btn_layout.addWidget(
            self.clear_btn
        )

        layout.addLayout(
            btn_layout
        )

        # -----------------------------------------------------
        # Log
        # -----------------------------------------------------

        self.log_label = QLabel(
            self.tr(
                "Log:"
            )
        )

        layout.addWidget(
            self.log_label
        )

        self.log_area = QPlainTextEdit()

        self.log_area.setReadOnly(
            True
        )

        layout.addWidget(
            self.log_area
        )

        self.setWidget(
            container
        )

    @staticmethod
    def tr(message):
        return QCoreApplication.translate(
            "DevPluginRefresher",
            message
        )

    def log(self, text):

        if hasattr(
            self,
            "log_area"
        ):

            self.log_area.appendPlainText(
                str(text)
            )

    def clear_log(self):

        if hasattr(
            self,
            "log_area"
        ):

            self.log_area.clear()

            self.log(
                self.tr(
                    "Log cleared."
                )
            )
