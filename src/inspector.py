from __future__ import annotations

from aqt import gui_hooks, mw, qt, webview

from .logger import log_widget_destroyed, logger
from .utils import get_icon
from .widgets import InspectorDock, InspectorSplitter


class BaseInspector(qt.QWidget):
    inspected_page: webview.AnkiWebPage
    label = qt.QLabel

    def __init__(self, parent: qt.QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(qt.Qt.WidgetAttribute.WA_DeleteOnClose)
        log_widget_destroyed(self)
        self.webview = qt.QWebEngineView(self)
        log_widget_destroyed(self.webview)
        self.setup_layout()

    def setup_layout(self) -> None:
        vbox = qt.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        topbar = self.create_topbar()
        vbox.addLayout(topbar)
        vbox.addWidget(self.webview)
        self.setLayout(vbox)

    def set_page(self, inspected_page: webview.AnkiWebPage) -> None:
        self.inspected_page = inspected_page
        # web channel
        channel = self.inspected_page.webChannel()
        self.webview.page().setWebChannel(channel)

        self.webview.loadFinished.connect(self.on_load_finished)
        self.webview.page().setInspectedPage(self.inspected_page)

    @qt.pyqtSlot(bool)
    def on_load_finished(self, ok: bool) -> None:
        logger.debug("on_load_finished")
        self._on_load_finished()
        self.webview.loadFinished.disconnect(self.on_load_finished)

    def _on_load_finished(self) -> None:
        pass

    @qt.pyqtSlot(int)
    def on_zoom_spinbox_value_changed(self, value: int) -> None:
        self.webview.setZoomFactor(value / 100)
        # https://stackoverflow.com/questions/12892129/how-to-prevent-qspinbox-from-automatically-highlighting-contents
        self.zoom_spinbox.lineEdit().deselect()

    def create_topbar(self) -> qt.QHBoxLayout:
        hbox = qt.QHBoxLayout()
        hbox.setSpacing(4)
        self.label = qt.QLabel(self)
        hbox.addWidget(self.label)
        hbox.addStretch()

        # Zoom
        self.zoom_spinbox = qt.QSpinBox(self)
        self.zoom_spinbox.setFocusPolicy(qt.Qt.FocusPolicy.NoFocus)
        self.zoom_spinbox.setRange(50, 150)
        self.zoom_spinbox.setValue(100)
        self.zoom_spinbox.setSingleStep(10)
        self.zoom_spinbox.setToolTip("Zoom level")
        self.zoom_spinbox.setSuffix(" %")
        self.zoom_spinbox.valueChanged.connect(
            self.on_zoom_spinbox_value_changed, qt.Qt.ConnectionType.QueuedConnection
        )
        hbox.addWidget(self.zoom_spinbox)

        # Buttons
        default_button_height = qt.QPushButton().sizeHint().height()
        button_size = qt.QSize(default_button_height, default_button_height)

        position_button = qt.QPushButton(self)
        position_button.setFocusPolicy(qt.Qt.FocusPolicy.NoFocus)
        position_button.setIcon(get_icon("icon/position.svg"))
        position_button.setToolTip("Change Position")
        position_menu = self.setup_position_menu()
        position_button.setMenu(position_menu)
        hbox.addWidget(position_button)

        close_button = qt.QPushButton(self)
        close_button.setFocusPolicy(qt.Qt.FocusPolicy.NoFocus)
        close_button.setMaximumSize(button_size)
        close_button.setIcon(get_icon("icon/close.svg"))
        close_button.setToolTip("Close Inspector")
        close_button.clicked.connect(self.on_close_button_clicked)
        hbox.addWidget(close_button)

        return hbox

    def inspect_element(self) -> None:
        self.inspected_page.triggerAction(qt.QWebEnginePage.WebAction.InspectElement)

    def set_label(self, text: str) -> None:
        self.label.setText(text)
        self.label.setToolTip(text)


class MainWindowInspector(BaseInspector):
    def __init__(self) -> None:
        self.dock = InspectorDock(mw)
        super().__init__(parent=self.dock)

        # https://doc.qt.io/qt-6/qdockwidget.html#appearance
        # > Custom size hints, minimum and maximum sizes and size policies
        # > should be implemented in the child widget.
        self.webview.setMinimumSize(200, 200)

        self.webview.urlChanged.connect(self.set_dock_title)
        self.dock.setWidget(self)
        self.inspected_page_changed = False

        gui_hooks.profile_did_open.append(self.on_profile_did_open)
        self.destroyed.connect(
            lambda *_: gui_hooks.profile_did_open.remove(self.on_profile_did_open)
        )

    def on_profile_did_open(self) -> None:
        # switching profiles with inspector open may hide dock widget
        self.dock.show()

    def _on_load_finished(self) -> None:
        self.inspect_element()
        if self.inspected_page_changed:
            self.set_dock_title()
        else:
            self.add_dock_to_mw()

    def add_dock_to_mw(self) -> None:
        # It seems that this process needs to be done at the very end
        # in order to accurately highlight the right-clicked element.
        mw.addDockWidget(qt.Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

    def set_dock_title(self) -> None:
        self.dock.setWindowTitle(self.inspected_page.title())

    @qt.pyqtSlot()
    def on_close_button_clicked(self) -> None:
        self.dock.close()

    def setup_position_menu(self) -> qt.QMenu:
        menu = qt.QMenu(self)
        act_right = qt.QAction("Right", menu)
        act_bottom = qt.QAction("Bottom", menu)
        act_float = qt.QAction("Float", menu)
        act_right.triggered.connect(lambda: self.dock.set_area("right"))
        act_bottom.triggered.connect(lambda: self.dock.set_area("bottom"))
        act_float.triggered.connect(lambda: self.dock.set_area("float"))
        menu.addAction(act_right)
        menu.addAction(act_bottom)
        menu.addAction(act_float)
        return menu


class SubWindowInspector(BaseInspector):
    def __init__(
        self,
        window_widget: qt.QWidget,
        target_widget: qt.QWidget,
        original_pos: int,
    ) -> None:
        super().__init__(parent=window_widget)
        self.window_widget = window_widget
        self.target_widget = target_widget

        self.original_pos = original_pos
        self.isFloating = False

    def _on_load_finished(self) -> None:
        self.set_label(f"Inspector({self.inspected_page.title()})")
        self.inspect_element()
        self.setup_splitter()

    @qt.pyqtSlot()
    def on_close_button_clicked(self) -> None:
        self.close()
        self.window_widget.layout().insertWidget(self.original_pos, self.target_widget)
        self.splitter.close()

    def setup_position_menu(self) -> qt.QMenu:
        menu = qt.QMenu(self)
        act_right = qt.QAction("Right", menu)
        act_bottom = qt.QAction("Bottom", menu)
        act_float = qt.QAction("Float", menu)
        act_right.triggered.connect(lambda: self.set_position("right"))
        act_bottom.triggered.connect(lambda: self.set_position("bottom"))
        act_float.triggered.connect(lambda: self.set_position("float"))
        menu.addAction(act_right)
        menu.addAction(act_bottom)
        menu.addAction(act_float)
        return menu

    def setup_splitter(self) -> None:
        self.setParent(self.window_widget)
        self.splitter = InspectorSplitter(self.window_widget)
        self.splitter.addWidget(self.target_widget)
        self.splitter.addWidget(self)
        self.splitter.equalize_sizes()
        self.window_widget.layout().insertWidget(self.original_pos, self.splitter, 1)

    def float(self) -> None:
        if self.isFloating:
            return
        self.isFloating = True
        self.window_widget.layout().insertWidget(self.original_pos, self.target_widget)
        self.setParent(None)
        self.splitter.close()
        self.show()

    def unfloat(self) -> None:
        if not self.isFloating:
            return
        self.setup_splitter()
        self.isFloating = False

    def set_position(self, where: str) -> None:
        """where: right | bottom | float"""
        if where == "right":
            self.unfloat()
            self.splitter.setOrientation(qt.Qt.Orientation.Horizontal)
            self.splitter.equalize_sizes()
        elif where == "bottom":
            self.unfloat()
            self.splitter.setOrientation(qt.Qt.Orientation.Vertical)
            self.splitter.equalize_sizes()
        elif where == "float":
            self.float()
