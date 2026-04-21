from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout
)
from qgis.PyQt.QtCore import Qt, QCoreApplication


class PluginSelectorDialog(QDialog):
    def __init__(self, plugin_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select plugin to reload")
        self.resize(380, 420)

        layout = QVBoxLayout(self)

        self.label = QLabel("Installed plugins:")
        layout.addWidget(self.label)

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter…")
        layout.addWidget(self.filter_edit)

        self.list_widget = QListWidget()
        self.list_widget.addItems(plugin_list)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.filter_edit.textChanged.connect(self.filter_list)

    def filter_list(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def selected_plugin(self):
        item = self.list_widget.currentItem()
        return item.text() if item else None

