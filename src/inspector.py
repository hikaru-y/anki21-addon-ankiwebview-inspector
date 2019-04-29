# Copyright: (c) 2019 Hikaru Y. <hkrysg@gmail.com>

from anki.hooks import addHook
from aqt import mw
from aqt.qt import *


TITLE = 'web dev tools'
FONT_SIZE = 12


class Inspector(QDockWidget):
    """ dockable web dev tools pane """

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setObjectName(title)
        self.setAllowedAreas(
            Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea|Qt.BottomDockWidgetArea)
        self.toggleViewAction().setText(f'show/hide "{title}"')
        self.web = None

    def setup_web(self, page):
        if self.web:
            self.web.deleteLater()
        self.web = QWebEngineView(mw)

        # font size
        ws = self.web.settings()
        ws.setFontSize(QWebEngineSettings.MinimumFontSize, FONT_SIZE)
        ws.setFontSize(QWebEngineSettings.MinimumLogicalFontSize, FONT_SIZE)
        ws.setFontSize(QWebEngineSettings.DefaultFontSize, FONT_SIZE)

        # "Uncaught ReferenceError: qt is not defined"を防ぐために
        # AnkiWebViewと同じwebChannelを使う
        channel = mw.web._page.webChannel()
        self.web.page().setWebChannel(channel)

        self.web.page().setInspectedPage(page)
        self.setWidget(self.web)
        self.show()

    @pyqtSlot()
    def on_anki_state_change(self, *_):
        """
        パネルを閉じた状態でAnkiのstateが変わったらwebをdelete
        """
        if self.isHidden():
            self.delete_web()
    
    def delete_web(self):
        if self.web:
            self.web.deleteLater()
            self.web = None


def on_contextMenuEvent(self, menu, pane):
    def handler():
        pane.setup_web(self.page())

    a = menu.addAction(f'{TITLE} - {self.title}')
    a.triggered.connect(handler)


def check_qt_version():
    """
    setInspectedPage, setDevToolsPageはQt5.11以降対応なのでチェックする
    """
    qt_ver = QT_VERSION_STR.split('.')
    if int(qt_ver[1]) < 11:
        return False
    else:
        return True


def main():
    if not check_qt_version():
        return

    pane = Inspector(TITLE, mw)
    mw.addDockWidget(Qt.RightDockWidgetArea, pane)

    # メインウィンドウ起動時にはパネルを閉じておく
    addHook('profileLoaded', pane.hide)
    # プロファイル切り替え時にwebをdelete
    addHook('unloadProfile', pane.delete_web)
    addHook('AnkiWebView.contextMenuEvent',
            lambda *args, pane=pane: on_contextMenuEvent(*args, pane))
    addHook('EditorWebView.contextMenuEvent',
            lambda *args, pane=pane: on_contextMenuEvent(*args, pane))
    addHook('beforeStateChange', pane.on_anki_state_change)


main()
