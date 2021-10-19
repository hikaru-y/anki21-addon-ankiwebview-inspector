# Copyright: (c) 2019 Hikaru Y. <hkrysg@gmail.com>

from anki.hooks import addHook
from aqt import mw
from aqt.qt import *


ADDON = 'AnkiWebView Inspector'
CONTEXT_MENU_ITEM_NAME = 'Inspect'
FONT_SIZE = 12
QDOCKWIDGET_STYLE = '''
    QDockWidget::title {
        padding-top: 0;
        padding-bottom: 0;
    }
'''


class Inspector(QDockWidget):
    """
    Dockable panel with Qt WebEngine Developer Tools
    """

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setObjectName(ADDON)
        self.setAllowedAreas(
              Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
        )
        self.toggleViewAction().setText('Toggle Inspector')
        # make the title bar thinner
        self.setStyleSheet(QDOCKWIDGET_STYLE)
        self.web = None
        self.setup_hooks()

    def setup_hooks(self):
        # メインウィンドウ起動時にはパネルを閉じておく
        addHook('profileLoaded', self.hide)
        # プロファイル切り替え時にwebをdelete
        addHook('unloadProfile', self.delete_web)
        addHook('AnkiWebView.contextMenuEvent', self.on_context_menu_event)
        addHook('EditorWebView.contextMenuEvent', self.on_context_menu_event)
        addHook('beforeStateChange', self.on_anki_state_change)

    def on_context_menu_event(self, web, menu):
        menu.addAction(CONTEXT_MENU_ITEM_NAME, lambda: self.setup_web(web.page()))

    def setup_web(self, page):
        if self.web:
            self.web.deleteLater()
        self.web = QWebEngineView(mw)
        self.web.setMinimumWidth(240)

        # font size
        ws = self.web.settings()
        ws.setFontSize(QWebEngineSettings.FontSize.MinimumFontSize, FONT_SIZE)
        ws.setFontSize(QWebEngineSettings.FontSize.MinimumLogicalFontSize, FONT_SIZE)
        ws.setFontSize(QWebEngineSettings.FontSize.DefaultFontSize, FONT_SIZE)

        # "Uncaught ReferenceError: qt is not defined"を防ぐために
        # AnkiWebViewと同じwebChannelを使う
        channel = mw.web._page.webChannel()
        self.web.page().setWebChannel(channel)

        self.web.page().setInspectedPage(page)
        self.setWidget(self.web)
        # make sure the panel is docked to main window when displaying
        self.setFloating(False)
        self.show()

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


def check_qt_version():
    """
    setInspectedPage, setDevToolsPageはQt5.11以降対応なのでチェックする
    """
    qt_major_ver, qt_minor_ver = [int(string) for string in QT_VERSION_STR.split('.')][:2]
    return (qt_major_ver == 5 and qt_minor_ver >= 11) or qt_major_ver == 6


def main():
    if not check_qt_version():
        return

    inspector = Inspector('', mw)
    mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, inspector)


main()
