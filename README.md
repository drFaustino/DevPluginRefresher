# DevPluginRefresher

DevPluginRefresher is a developer‑oriented QGIS plugin that allows rapid reloading of any installed Python plugin without restarting QGIS.  
It provides a custom dockable interface, auto‑reload options, and a detailed log panel to streamline plugin development workflows.

---

## Features

- **Reload any installed Python plugin instantly**
  Avoid restarting QGIS during development.

- **Custom dock widget**
  Includes plugin selector, reload button, auto‑reload toggle, and log area.

- **Auto‑reload on file change**
  Automatically reloads the selected plugin when `.py` files in its directory are modified.

- **Detailed logging**
  All actions and reload events are recorded in a dedicated log panel.

- **Persistent plugin selection**
  The last selected plugin is remembered across sessions.

- **Clean and developer‑friendly UI**
  Designed for fast iteration and minimal friction.

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
