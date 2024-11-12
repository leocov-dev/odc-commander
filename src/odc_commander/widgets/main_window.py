from pathlib import Path
from typing import Any, cast

from PySide6.QtCore import QSize, QTimer, Signal
from PySide6.QtGui import QAction, QKeySequence, Qt
from PySide6.QtSerialPort import QSerialPortInfo
from PySide6.QtWidgets import QFileDialog, QTabWidget, QVBoxLayout, QWidget
from pyside_app_core import log
from pyside_app_core.app.application_service import AppMetadata
from pyside_app_core.services.serial_service import SerialService
from pyside_app_core.ui.standard.main_window import MainToolbarWindow
from pyside_app_core.ui.widgets.connection_manager import ConnectionManager, PortData
from pyside_app_core.ui.widgets.core_icon import CoreIcon
from pyside_app_core.ui.widgets.layout import HLine
from pyside_app_core.ui.widgets.preferences_manager import PreferencesDialog
from pyside_app_core.utils.cursor import set_cursor
from pyside_app_core.utils.time_ms import SECONDS

from odc_commander.arduino.uploader import ArduinoUploader, SketchData, SketchMap
from odc_commander.arduino.vendor_map import ProductData, ProductMap, VENDOR_MAP, VendorData
from odc_commander.interfaces.controller import Controller, ControllerView, SwitchedController


def _port_data_mapper(port_info: QSerialPortInfo) -> PortData:
    display_name = port_info.systemLocation()

    if product_data := (
            VENDOR_MAP.get(port_info.vendorIdentifier(), cast(VendorData, {}))
                    .get("products", cast(ProductMap, {}))
                    .get(port_info.productIdentifier(), cast(ProductData, {}))
    ):
        display_name = f"{product_data.get("display_name")} ({port_info.serialNumber()[-6:]})"

    return PortData(display_name, product_data.get("board", "unknown:unknown"))


class OdcMainWindow(MainToolbarWindow):
    tab_changed = Signal(int)
    debug_mode = Signal(bool)

    request_new = Signal()
    request_save = Signal()
    request_save_as = Signal(Path)
    request_load = Signal(Path)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(AppMetadata.name)

        self._serial_com: SerialService | None = None

        self.setMinimumSize(640, 200)

        self.statusBar().showMessage(f"v{AppMetadata.version}")

        central = QWidget(self)
        self.setCentralWidget(central)

        _ly = QVBoxLayout()
        _ly.setSpacing(10)
        _ly.setContentsMargins(0, 0, 0, 0)
        central.setLayout(_ly)

        self._main_tabs = QTabWidget(self)
        _ly.addWidget(self._main_tabs)

        _ly.addWidget(HLine(self))

        _ly_controls = QVBoxLayout()
        _ly_controls.setContentsMargins(10, 0, 10, 5)
        _ly.addLayout(_ly_controls)

        # ----
        self._tab_sketch_map: SketchMap = {}
        self._uploader = ArduinoUploader(
            parent=self,
        )
        self._uploader.setDisabled(True)
        _ly_controls.addWidget(self._uploader)

        # ----
        self._connection_manager = ConnectionManager(
            autoconnect=True,
            port_data_mapper=_port_data_mapper,
            remember_last_connection=True,
            parent=self,
        )
        _ly_controls.addWidget(self._connection_manager)

        # -----
        QTimer.singleShot(int(1.25 * SECONDS), self._connection_manager.request_port_refresh)

        self._main_tabs.currentChanged.connect(self.tab_changed)
        self._main_tabs.currentChanged.connect(self._on_tab_changed)
        self._connection_manager.port_changed.connect(self._port_changed)
        self._uploader.about_to_upload.connect(self._about_to_upload)
        self._uploader.upload_complete.connect(self._upload_complete)

    @property
    def connection_manager(self) -> ConnectionManager:
        return self._connection_manager

    @property
    def serial_com(self) -> SerialService:
        if not self._serial_com:
            raise RuntimeError("Serial Service must be set...")
        return self._serial_com

    def set_serial_service(self, com: SerialService) -> None:
        self._serial_com = com

    def add_controller_tab(
        self,
        view: ControllerView[Any],
        sketch: Path | None = None,
        uploader_btn_text: str = "",
        *,
        readonly: bool = False,
    ) -> None:
        view.setParent(self)
        tab_index = self._main_tabs.addTab(view, view.TAB_NAME or view.__class__.__name__)

        self._tab_sketch_map[tab_index] = {
            "sketch":            sketch,
            "uploader_btn_text": uploader_btn_text,
            "readonly":          readonly,
        }

        with (
            self.menu_bar.menu("View") as view_menu,
            view_menu.menu("Tools") as tools_menu,
            tools_menu.action(view.__class__.__name__) as view_action,
        ):
            view_action.triggered.connect(lambda _ti=tab_index: self._main_tabs.setCurrentIndex(_ti))

    def _on_tab_changed(self, tab_index: int) -> None:
        tab_data: SketchData | dict[Any, Any] = self._tab_sketch_map.get(tab_index, {})

        self._uploader.set_current_data(
            tab_data.get("sketch", None),
            tab_data.get("uploader_btn_text", ""),
            tab_data.get("readonly", False),
        )

    def current_tab_index(self) -> int:
        return self._main_tabs.currentIndex()

    def tab_by_index(self, index: int) -> SwitchedController:
        view = cast(ControllerView, self._main_tabs.widget(index))
        return view.controller

    def _port_changed(self, port_info: QSerialPortInfo | None, board: str) -> None:
        self._uploader.setEnabled(port_info is not None)
        self._uploader.set_active_port(port_info, board)

    def _about_to_upload(self) -> None:
        self._was_connected = self.serial_com.is_connected
        self._uploader.setDisabled(True)
        self._connection_manager.setDisabled(True)
        self.serial_com.close_connection()

    def _upload_complete(self) -> None:
        self._uploader.setEnabled(True)
        self._connection_manager.setEnabled(True)
        if self._connection_manager.current_port and self._was_connected:
            self.serial_com.open_connection(self._connection_manager.current_port)

    def _restore_state(self) -> None:
        super()._restore_state()
        self._main_tabs.setCurrentIndex(self.get_setting("currentTabIndex", 0, int))

    def _store_state(self) -> None:
        super()._store_state()
        self.store_setting("currentTabIndex", self.current_tab_index())

    def _build_menus(self) -> None:
        # init menus in correct order

        # ----------------------------------------------------------------------
        # file --------
        with self._menu_bar.menu("File") as file_menu:
            with file_menu.action("Preferences...", CoreIcon(":/core/iconoir/settings.svg")) as self._prefs_action:
                self._prefs_action.setMenuRole(QAction.MenuRole.PreferencesRole)
                self._prefs_action.triggered.connect(lambda: self.show_app_modal_dialog(PreferencesDialog()))

            with file_menu.action("New", CoreIcon(":/core/iconoir/page-plus-in.svg")) as self._new_action:
                self._new_action.triggered.connect(lambda: self.request_new.emit())
                self._new_action.setShortcut(QKeySequence.StandardKey.New)
            with file_menu.action("Open...", CoreIcon(":/core/iconoir/folder.svg")) as self._open_action:
                self._open_action.triggered.connect(self._open_browser)
                self._open_action.setShortcut(QKeySequence.StandardKey.Open)
            with file_menu.action("Save", CoreIcon(":/core/iconoir/floppy-disk.svg")) as self._save_action:
                self._save_action.triggered.connect(self._request_save)
                self._save_action.setShortcut(QKeySequence.StandardKey.Save)
            with file_menu.action("Save As...", CoreIcon(":/core/iconoir/page-edit.svg")) as self._save_as_action:
                self._save_as_action.triggered.connect(self._save_as_browser)
                self._save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)

        # ----------------------------------------------------------------------
        # edit --------
        with self.menu_bar.menu("Edit"):
            pass

        # ----------------------------------------------------------------------
        # view -------
        with self.menu_bar.menu("View"):
            pass

        # ----------------------------------------------------------------------
        # help ----------
        # with (
        #     self._menu_bar.menu("Help") as help_menu,
        #     help_menu.action("Documentation") as about_action,
        # ):
        #     about_action.triggered.connect(self._show_help)

    def _build_toolbar(self) -> None:
        self.tool_bar.setIconSize(QSize(20, 20))
        self.tool_bar.setSpacing(5)

        self.tool_bar.add_spacer(5)

        self.tool_bar.addAction(self._new_action)
        self.tool_bar.addAction(self._open_action)
        self.tool_bar.addAction(self._save_action)
        self.tool_bar.addAction(self._save_as_action)

        self.tool_bar.add_stretch()
        self.tool_bar.addAction(self._prefs_action)
        self.tool_bar.add_spacer(5)

    def _save_as_browser(self) -> None:
        file, _ = QFileDialog.getSaveFileName(
            self,
            "Save ODC Project",
            str(AppMetadata.documents_dir),
            "ODC Project (*.odc)",
        )
        if not file:
            log.debug(f"saving project canceled")
            return

        log.debug(f"saving project to: {file}")
        self.request_save_as.emit(Path(file))

    def _open_browser(self) -> None:
        AppMetadata.documents_dir.mkdir(exist_ok=True, parents=True)

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open ODC Project",
            str(AppMetadata.documents_dir),
            "ODC Projects (*.odc)",
            "",
            QFileDialog.Option.ReadOnly,
        )

        if not path:
            log.debug("open project canceled")
            return

        self.request_load.emit(Path(path))

    def _request_save(self) -> None:
        set_cursor(Qt.CursorShape.WaitCursor)
        self.tool_bar.get_action("Save").setDisabled(True)
        self.request_save.emit()
