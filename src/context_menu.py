from __future__ import annotations

from typing import cast

from aqt import gui_hooks, mw, qt
from aqt.editor import EditorWebView
from aqt.webview import AnkiWebView

from . import consts
from .inspector import MainWindowInspector, SubWindowInspector
from .widgets import InspectorDock
from .window_info import windows


def inspect_main_window(inspected_webview: AnkiWebView) -> None:
    page = inspected_webview.page()
    assert page is not None

    if page.devToolsPage():
        page.triggerAction(qt.QWebEnginePage.WebAction.InspectElement)
    else:
        assert mw is not None

        if dock := mw.findChild(InspectorDock):
            inspector = dock.widget()
            assert isinstance(inspector, MainWindowInspector)

            inspector.inspected_page_changed = True
        else:
            inspector = MainWindowInspector()
        inspector.set_page(page)


def inspect_sub_window(
    inspected_webview: AnkiWebView | EditorWebView,
    window_widget: qt.QWidget,
    target_widget: qt.QWidget,
    insert_pos: int,
) -> None:
    page = inspected_webview.page()
    assert page is not None

    if page.devToolsPage():
        page.triggerAction(qt.QWebEnginePage.WebAction.InspectElement)
    else:
        target_widget.setSizePolicy(
            qt.QSizePolicy.Policy.Expanding, qt.QSizePolicy.Policy.Expanding
        )
        inspector = SubWindowInspector(window_widget, target_widget, insert_pos)
        inspector.set_page(page)
        layout = cast(qt.QBoxLayout, window_widget.layout())
        layout.insertWidget(insert_pos, inspector.splitter, 1)


def on_webview_will_show_context_menu(webview: AnkiWebView, menu: qt.QMenu) -> None:
    window = webview.window()
    assert window is not None

    if window_info := next(
        (i for i in windows if type(window) is i.get_widget()), None
    ):
        if window_info.main_window:
            # mw.web, mw.bottomWeb, mw.toolbarWeb
            menu.addAction(
                consts.CONTEXT_MENU_ITEM_LABEL,
                lambda: inspect_main_window(webview),
            )
        else:
            # clayout, previewer, stats, etc.
            target = window_info.get_target(window, webview)
            insert_pos = window_info.insert_pos
            menu.addAction(
                consts.CONTEXT_MENU_ITEM_LABEL,
                lambda window=window: inspect_sub_window(
                    webview, window, target, insert_pos
                ),
            )


def on_editor_will_show_context_menu(
    editor_webview: EditorWebView, menu: qt.QMenu
) -> None:
    menu.addAction(
        consts.CONTEXT_MENU_ITEM_LABEL,
        lambda: inspect_sub_window(
            editor_webview, editor_webview.editor.widget, editor_webview, 0
        ),
    )


def register_context_menu() -> None:
    gui_hooks.webview_will_show_context_menu.append(on_webview_will_show_context_menu)
    gui_hooks.editor_will_show_context_menu.append(on_editor_will_show_context_menu)
