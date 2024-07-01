from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget
from pyside_app_core.qt.application_service import AppMetadata
from pyside_app_core.qt.standard import MainWindow
from pyside_app_core.qt.widgets.connection_manager import ConnectionManager
from pyside_app_core.utils.time_ms import SECONDS

from odc_commander.interfaces.controller import ControllerView


class OdcMainWindow(MainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setMinimumSize(420, 128)

        self.statusBar().showMessage(f"v{AppMetadata.version}")

        central = QWidget(self)
        self.setCentralWidget(central)

        _ly = QVBoxLayout()
        _ly.setSpacing(0)
        _ly.setContentsMargins(0, 0, 0, 0)
        central.setLayout(_ly)

        self._main_tabs = QTabWidget(self)
        _ly.addWidget(self._main_tabs)

        self._connection_manager = ConnectionManager(parent=self)
        _ly.addWidget(self._connection_manager)

        # -----
        QTimer.singleShot(1 * SECONDS, self._connection_manager.request_port_refresh)

        # TODO: good idea???
        # self._main_tabs.currentChanged.connect(self.adjustSize)

    @property
    def connection_manager(self) -> ConnectionManager:
        return self._connection_manager

    def _build_menus(self) -> None:
        # init menus in correct order
        with self.menu_bar.menu("View"):
            pass

    def add_controller_tab(self, view: ControllerView) -> None:
        view.setParent(self)
        tab_index = self._main_tabs.addTab(view, view.TAB_NAME or view.__class__.__name__)

        with (
            self.menu_bar.menu("View") as view_menu,
            view_menu.menu("Tools") as tools_menu,
            tools_menu.action(view.__class__.__name__) as view_action,
        ):
            view_action.triggered.connect(lambda: self._main_tabs.setCurrentIndex(tab_index))
