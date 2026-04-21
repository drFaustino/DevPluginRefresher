from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QCheckBox, QPlainTextEdit
)
from qgis.PyQt.QtCore import QCoreApplication
import os
from qgis.PyQt.QtGui import QIcon

class RefresherDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.setWindowTitle("DevPluginRefresher")
        self.setWindowIcon(QIcon(icon_path))

        container = QWidget()
        layout = QVBoxLayout(container)

        # Plugin selector
        layout.addWidget(QLabel("Select plugin (loaded):"))
        self.plugin_combo = QComboBox()
        layout.addWidget(self.plugin_combo)

        # Auto reload checkbox
        self.auto_reload = QCheckBox("Auto-reload on .py change")
        layout.addWidget(self.auto_reload)

        # Reload + Clear buttons
        btn_layout = QHBoxLayout()
        self.reload_btn = QPushButton("Reload now")
        self.clear_btn = QPushButton("Clear log")
        btn_layout.addWidget(self.reload_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)

        # Log area
        layout.addWidget(QLabel("Log:"))
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.setWidget(container)

    def log(self, text: str):
        self.log_area.appendPlainText(text)
    
    def clear_log(self):
        self.log_area.clear()
        self.log("Log cleared.")


