from __future__ import annotations

from aqt import gui_hooks, mw, qt, webview
from aqt.editor import EditorWebView
from aqt.webview import AnkiWebView

from . import consts
from .inspector import MainWindowInspector, SubWindowInspector
from .widgets import InspectorDock
from .window_info import windows


def inspect_main_window(inspected_page: webview.AnkiWebPage) -> None:
    if inspected_page.devToolsPage():
        inspected_page.triggerAction(qt.QWebEnginePage.WebAction.InspectElement)
    else:
        inspector: MainWindowInspector
        dock: InspectorDock | None
        if dock := mw.findChild(InspectorDock):
            inspector = dock.widget()
            inspector.inspected_page_changed = True
        else:
            inspector = MainWindowInspector()
        inspector.set_page(inspected_page)


def inspect_sub_window(
    inspected_page: webview.AnkiWebPage,
    window_widget: qt.QWidget,
    target_widget: qt.QWidget,
    insert_pos: int,
) -> None:
    if inspected_page.devToolsPage():
        inspected_page.triggerAction(qt.QWebEnginePage.WebAction.InspectElement)
    else:
        target_widget.setSizePolicy(
            qt.QSizePolicy.Policy.Expanding, qt.QSizePolicy.Policy.Expanding
        )
        inspector = SubWindowInspector(window_widget, target_widget, insert_pos)
        inspector.set_page(inspected_page)
        layout: qt.QBoxLayout = window_widget.layout()
        layout.insertWidget(insert_pos, inspector.splitter, 1)


def on_webview_will_show_context_menu(webview: AnkiWebView, menu: qt.QMenu) -> None:
    window = webview.window()
    if window_info := next(
        (i for i in windows if type(window) is i.get_widget()), None
    ):
        if window_info.main_window:
            # mw.web, mw.bottomWeb, mw.toolbarWeb
            menu.addAction(
                consts.CONTEXT_MENU_ITEM_LABEL,
                lambda: inspect_main_window(webview.page()),
            )
        else:
            # clayout, previewer, stats, etc.
            target: qt.QWidget = getattr(window, window_info.target, webview)
            insert_pos = window_info.insert_pos
            menu.addAction(
                consts.CONTEXT_MENU_ITEM_LABEL,
                lambda: inspect_sub_window(webview.page(), window, target, insert_pos),
            )


def on_editor_will_show_context_menu(
    editor_webview: EditorWebView, menu: qt.QMenu
) -> None:
    menu.addAction(
        consts.CONTEXT_MENU_ITEM_LABEL,
        lambda: inspect_sub_window(
            editor_webview.page(), editor_webview.editor.widget, editor_webview, 0
        ),
    )


def register_context_menu() -> None:
    gui_hooks.webview_will_show_context_menu.append(on_webview_will_show_context_menu)
    gui_hooks.editor_will_show_context_menu.append(on_editor_will_show_context_menu)
