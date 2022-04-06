from __future__ import annotations

from dataclasses import dataclass
from operator import attrgetter

import aqt
from aqt import qt

from .logger import logger


@dataclass
class WindowInfo:
    dotted_attr: str
    target: str = ""
    insert_pos: int = 0
    main_window: bool = False

    def get_widget(self) -> qt.Qwidget | None:
        try:
            return attrgetter(self.dotted_attr)(aqt)
        except Exception as e:
            logger.debug(e)
            return None


windows = (
    WindowInfo(dotted_attr="main.AnkiQt", main_window=True),
    WindowInfo(dotted_attr="browser.card_info.CardInfoDialog"),
    WindowInfo(dotted_attr="browser.previewer.BrowserPreviewer"),
    WindowInfo(dotted_attr="changenotetype.ChangeNotetypeDialog"),
    WindowInfo(dotted_attr="clayout.CardLayout", target="mainArea", insert_pos=1),
    WindowInfo(dotted_attr="deckoptions.DeckOptionsDialog"),
    WindowInfo(dotted_attr="emptycards.EmptyCardsDialog"),
    WindowInfo(dotted_attr="fields.FieldDialog"),
    WindowInfo(dotted_attr="stats.NewDeckStats"),
)
