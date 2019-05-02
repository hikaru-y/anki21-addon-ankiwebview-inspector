# AnkiWebView Inspector

This is an add-on for [Anki version 2.1](https://apps.ankiweb.net/). It provides an inspector panel using [Qt WebEngine Developer Tools](https://doc.qt.io/qt-5/qtwebengine-debugging.html#qt-webengine-developer-tools). It is similar to *Google chrome developer tools*. It makes it easy to inspect and debug the webviews of Anki. It might be useful when developing an add-on or creating complex card templates.

### Requirements
This add-on requires Qt version 5.11 or higher. To detect the Qt version, go to the Anki "Help" menu > "About...".

### Usage
This add-on adds an item named "**Inspect**" to the right-click context menu on an AnkiWebView area, including the following area:

- **main webview** (the middle area of the review screen, the deck overview screen, and the deck screen)
- **top toolbar** (the upper area, which contains commands of Decks, Add, Browse, Stats, and Sync)
- **bottom toolbar** (the buttons area at the bottom)
- **editor** (the middle area of "Add" or "Current Edit" dialog)

When clicking the item, an **Inspector** panel will be shown. The panel can be docked inside the Anki main window or floated as a top-level window. It moves when the title bar is dragged. It is docked or undocked when the title bar is double-clicked.

### Screenshots
![context menu](/screenshots/screenshot_01.png)
- - -
![panel](/screenshots/screenshot_02.png)

### Note
**Without** this add-on, you can debug the webviews using an external *Google Chrome* instance. For more information, see [Writing Anki 2.1.x Add-ons#Webview Changes](https://apps.ankiweb.net/docs/addons.html#_webview_changes).

### Changelog
See [CHANGELOG.md](/CHANGELOG.md).
