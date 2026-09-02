# DevPluginRefresher

DevPluginRefresher is a developer-oriented QGIS plugin that allows rapid reloading of installed Python plugins without restarting QGIS.

It provides a dockable interface for selecting plugins, manually triggering reloads, optionally monitoring .py file changes for automatic reloads, and viewing detailed activity logs. It is designed to reduce development downtime and make the QGIS plugin development workflow faster and more efficient.

---

## Features

- **Reload installed Python plugins**
  Reload a loaded Python plugin without restarting QGIS.

- **Dockable developer interface**
  Provides a clean interface with plugin selection, manual reload, auto-reload controls, and a detailed log panel.

- **Automatic reload on .py changes**
  Optionally monitors the selected plugin directory and automatically reloads the plugin when Python source files change.

- **Detailed logging**
  Reload operations, file changes, errors, and other relevant events are displayed in the integrated log panel.

- **Persistent plugin selection**
  The last selected plugin is remembered across QGIS sessions.

- **Persistent auto-reload setting**
  The auto-reload preference is restored automatically when the plugin is opened again.

- **Self-reload support**
  DevPluginRefresher can reload itself while preserving the selected plugin and auto-reload settings.

- **English and Italian interface**
  The plugin automatically selects English or Italian according to the QGIS user locale.

- **Developer-focused workflow**
  Designed to reduce repetitive QGIS restarts and speed up plugin development and testing.

---

## How It Works

1. Open the plugin from the QGIS Plugins menu or toolbar.
2. Select a loaded Python plugin from the dropdown list.
3. Click **Reload now** to reload it manually.
4. Enable **Auto‑reload on .py change** to reload automatically when source files change.
5. Use **Clear log** to reset the log panel.

---

## Requirements

- QGIS 4.x
- Python 3
- Qt6 / PyQt6

---

## Installation

1. Copy the plugin folder `DevPluginRefresher` into your QGIS profile directory: 
    <user profile>/python/plugins/

2. Restart QGIS.
3. Enable **DevPluginRefresher** from the Plugin Manager.

---

## Author

**Dr. Geol. Faustino Cetraro**  

---

## License

This plugin is released under the GNU General Public License v3 or later.
