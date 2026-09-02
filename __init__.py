import os

from qgis.PyQt.QtCore import QSettings, QTranslator
from qgis.PyQt.QtWidgets import QApplication


_translator = None


def classFactory(iface):
    global _translator

    _translator = _load_translation()

    from .dev_plugin_refresher import DevPluginRefresher

    return DevPluginRefresher(iface)


def _load_translation():
    app = QApplication.instance()

    if app is None:
        return None

    locale = QSettings().value(
        "locale/userLocale",
        "en_US"
    )

    locale = str(locale)
    language = locale.split("_")[0].lower()

    # Lingue supportate dal plugin
    if language not in ("it", "en"):
        language = "en"

    plugin_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    translation_file = os.path.join(
        plugin_dir,
        "i18n",
        f"DevPluginRefresher_{language}.qm"
    )

    if not os.path.isfile(translation_file):
        return None

    translator = QTranslator()

    if translator.load(translation_file):
        app.installTranslator(translator)
        return translator

    return None
