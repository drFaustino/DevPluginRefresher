from .dev_plugin_refresher import DevPluginRefresher

def classFactory(iface):
    return DevPluginRefresher(iface)
