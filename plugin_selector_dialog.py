from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)


class PluginSelectorDialog(QDialog):

    def __init__(self, plugin_list, parent=None):
        super().__init__(parent)

        self.setWindowTitle(
            self.tr("Select plugin to reload")
        )

        self.resize(380, 420)

        layout = QVBoxLayout(self)

        self.label = QLabel(
            self.tr("Installed plugins:")
        )
        layout.addWidget(self.label)

        self.filter_edit = QLineEdit()

        self.filter_edit.setPlaceholderText(
            self.tr("Filter…")
        )

        layout.addWidget(self.filter_edit)

        self.list_widget = QListWidget()
        self.list_widget.addItems(plugin_list)

        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()

        self.ok_btn = QPushButton(
            self.tr("OK")
        )

        self.cancel_btn = QPushButton(
            self.tr("Cancel")
        )

        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(
            self.accept
        )

        self.cancel_btn.clicked.connect(
            self.reject
        )

        self.filter_edit.textChanged.connect(
            self.filter_list
        )

    @staticmethod
    def tr(message):
        return QCoreApplication.translate(
            "DevPluginRefresher",
            message
        )

    def filter_list(self, text):
        text = text.lower()

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)

            item.setHidden(
                text not in item.text().lower()
            )

    def selected_plugin(self):
        item = self.list_widget.currentItem()

        return item.text() if item else None
