from __future__ import annotations

from dataclasses import dataclass
from operator import attrgetter
from typing import TYPE_CHECKING

import aqt
from aqt import qt

from .logger import logger

if TYPE_CHECKING:
    from aqt.webview import AnkiWebView


@dataclass
class WindowInfo:
    window_attr: str
    target_attr: str = ""
    insert_pos: int = 0
    main_window: bool = False

    def get_widget(self) -> qt.QWidget | None:
        try:
            return attrgetter(self.window_attr)(aqt)
        except Exception as e:
            logger.debug(e)
            return None

    def get_target(self, window: qt.QWidget, webview: AnkiWebView) -> qt.QWidget:
        if self.target_attr:
            return attrgetter(self.target_attr)(window)
        else:
            return webview


windows = (
    WindowInfo(window_attr="main.AnkiQt", main_window=True),
    WindowInfo(window_attr="browser.card_info.CardInfoDialog"),
    WindowInfo(window_attr="browser.previewer.BrowserPreviewer"),
    WindowInfo(window_attr="changenotetype.ChangeNotetypeDialog"),
    WindowInfo(window_attr="clayout.CardLayout", target_attr="mainArea", insert_pos=1),
    WindowInfo(window_attr="deckoptions.DeckOptionsDialog"),
    WindowInfo(window_attr="emptycards.EmptyCardsDialog"),
    WindowInfo(window_attr="fields.FieldDialog"),
    WindowInfo(window_attr="stats.NewDeckStats"),
    WindowInfo(window_attr="addons.ConfigEditor", target_attr="form.splitter"),
)
