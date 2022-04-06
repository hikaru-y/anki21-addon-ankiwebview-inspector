from __future__ import annotations

from aqt import qt

from . import consts
from .logger import log_widget_destroyed


class InspectorDock(qt.QDockWidget):
    def __init__(self, parent: qt.QMainWindow) -> None:
        super().__init__(parent)
        self.setObjectName(consts.ADDON_NAME)
        self.setAttribute(qt.Qt.WidgetAttribute.WA_DeleteOnClose)
        log_widget_destroyed(self)
        self.parent = parent

        # make sure the panel is docked to main window at startup
        self.setFloating(False)

        # allowed areas
        self.setAllowedAreas(
            qt.Qt.DockWidgetArea.RightDockWidgetArea
            | qt.Qt.DockWidgetArea.BottomDockWidgetArea
        )

    def toggle_area(self) -> None:
        """Right <-> Bottom"""
        if self.isFloating():
            self.setFloating(False)
        else:
            new_area = (
                self.parent.dockWidgetArea(self)  # current area
                ^ qt.Qt.DockWidgetArea.RightDockWidgetArea
                ^ qt.Qt.DockWidgetArea.BottomDockWidgetArea
            )
            self.parent.addDockWidget(new_area, self)


class InspectorSplitter(qt.QSplitter):
    def __init__(self, parent: qt.QDialog) -> None:
        super().__init__(parent)
        self.setObjectName(consts.ADDON_NAME)
        self.setAttribute(qt.Qt.WidgetAttribute.WA_DeleteOnClose)
        log_widget_destroyed(self)
        self.setChildrenCollapsible(False)
        self.setOrientation(qt.Qt.Orientation.Vertical)

    def toggle_orientation(self) -> None:
        """Right <-> Bottom"""
        new_orientation = (
            self.orientation()
            ^ qt.Qt.Orientation.Vertical
            ^ qt.Qt.Orientation.Horizontal
        )
        self.setOrientation(new_orientation)
        self.equalize_sizes()

    def equalize_sizes(self) -> None:
        # https://stackoverflow.com/questions/43831474/how-to-equally-distribute-the-width-of-qsplitter
        self.setSizes([10000, 10000])
