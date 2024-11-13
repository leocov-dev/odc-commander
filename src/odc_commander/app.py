import typing
from pathlib import Path
from typing import cast

from loguru import logger
from PySide6.QtSerialPort import QSerialPortInfo
from pyside_app_core.app.application_service import AppMetadata
from pyside_app_core.errors import excepthook
from pyside_app_core.log import configure_get_logger_func
from pyside_app_core.services.preferences_service import PreferencesService, PrefGroup, PrefItem, PrefSection
from pyside_app_core.services.serial_service import SerialService
from pyside_app_core.ui.prefs import PathWithPlaceholder
from pyside_app_core.ui.standard.error_dialog import ErrorDialog
from pyside_app_core.ui.widgets.base_app import BaseApp
from pyside_app_core.utils.cursor import clear_cursor
from pyside_app_core.utils.signals import OneToManySwitcher

from odc_commander import __version__, controllers, DATA_DIR
from odc_commander.arduino.sketch import get_sketch
from odc_commander.arduino.vendor_map import VENDOR_MAP
from odc_commander.commands import CobsTranscoder, LegacyTranscoder
from odc_commander.interfaces.controller import SerialConfig
from odc_commander.project.project_service import ProjectService
from odc_commander.widgets.controller_views.calibration_input_view import CalibrationInputView
from odc_commander.widgets.controller_views.calibration_output_view import CalibrationOutputView
from odc_commander.widgets.controller_views.runtime_view import RuntimeView
from odc_commander.widgets.main_window import OdcMainWindow

if typing.TYPE_CHECKING:
    from PySide6.QtGui import QAction

# ------------------------------------------------------------------------------
configure_get_logger_func(lambda: logger)

excepthook.install_excepthook(ErrorDialog)

# ------------------------------------------------------------------------------
AppMetadata.init(
    "com.odc.commander",
    "ODC Commander",
    __version__,
    icon_resource=":/odc/app/icon.png",
    help_url="https://github.com/leocov-dev/odc-commander",
    bug_report_url="https://github.com/leocov-dev/odc-commander/issues",
    oss_licenses=[":/odc/licenses/arduino-cli.md"],
)


# ------------------------------------------------------------------------------
def _port_filter(ports: list[QSerialPortInfo]) -> list[QSerialPortInfo]:
    filtered = []

    port_names = [p.portName() for p in ports]

    for port in ports:
        if "bluetooth" in port.portName().lower():
            continue

        if port.portName().startswith("cu.") and port.portName().replace("cu.", "tty.") in port_names:
            continue

        if port.vendorIdentifier() not in VENDOR_MAP:
            continue

        if products := VENDOR_MAP[port.vendorIdentifier()]["products"]:  # noqa: SIM102
            if port.productIdentifier() not in products:
                continue

        filtered.append(port)

    return filtered


class OdcCommanderApp(BaseApp[OdcMainWindow]):
    """Main App"""

    @property
    def project(self) -> ProjectService:
        return self._project

    def __init__(self, *, debug: bool = False) -> None:
        super().__init__(resources_rcc=DATA_DIR / "resources.rcc")

        # ---
        # project service
        self._project = ProjectService(self)
        self._update_save_action_state()

        self._project.unsaved_changes.connect(lambda n: self._main_window.setWindowTitle(f"{n} *"))
        self._project.project_loaded.connect(self._project_loaded)
        self._project.project_saved.connect(self._project_saved)

        self._main_window.request_new.connect(self._project.new)
        self._main_window.request_save.connect(self._project.save)
        self._main_window.request_save_as.connect(self._project.save_as)
        self._main_window.request_load.connect(self._project.load)

        # ---
        # serial service
        self._serial_com = SerialService(parent=self)
        self._serial_com.set_port_filter(_port_filter)

        self._main_window.set_serial_service(self._serial_com)

        # ----
        _sw_data = OneToManySwitcher(self._serial_com.com_data, parent=self)
        _serial_config = SerialConfig(self._serial_com, _sw_data)

        # ---
        # controllers
        self._runtime_controller = controllers.Runtime(
            _serial_config,
            LegacyTranscoder,
            parent=self,
        )
        self._project.register_component(self._runtime_controller)
        self._runtime_view = RuntimeView(self._runtime_controller)

        # ---
        # tab views
        self._main_window.add_controller_tab(
            self._runtime_view,
            None,
            "Upload Firmware",
            readonly=False,
        )
        if debug:
            # ---
            self._calibration_input_controller = controllers.CalibrationInput(
                _serial_config,
                CobsTranscoder,
                parent=self,
            )
            self._project.register_component(self._calibration_input_controller)
            self._calibration_input_view = CalibrationInputView(self._calibration_input_controller)
            self._main_window.add_controller_tab(
                self._calibration_input_view,
                get_sketch("calibration-input-output"),
                "Upload Calibration Firmware",
                readonly=True,
            )
            # ---
            self._calibration_output_controller = controllers.CalibrationOutput(
                _serial_config,
                CobsTranscoder,
                parent=self,
            )
            self._project.register_component(self._calibration_output_controller)
            self._calibration_output_view = CalibrationOutputView(self._calibration_output_controller)
            self._main_window.add_controller_tab(
                self._calibration_output_view,
                get_sketch("calibration-input-output"),
                "Upload Calibration Firmware",
                readonly=True,
            )

        # ---
        # serial data readers
        self._serial_com.register_reader(self._main_window.connection_manager)

        # ---
        # tabs
        self._main_window.tab_changed.connect(_sw_data.set_current_index)
        self._main_window.tab_changed.connect(self._on_tab_changed)
        self._runtime_controller.activated()
        # connection management
        self._main_window.connection_manager.refresh_ports.connect(self._serial_com.scan_for_ports)
        self._main_window.connection_manager.request_connect.connect(self._serial_com.open_connection)
        self._main_window.connection_manager.request_disconnect.connect(self._serial_com.close_connection)
        # debug
        SerialService.DEBUG = debug

        # ---
        if (
            (pref := PreferencesService.fqdn_to_pref("app.gen.open-last-proj"))
            and isinstance(pref, PrefItem)
            and pref.value
            and (last := cast(Path | None, self.project.get_setting("last-open-project", None)))
        ):
            self.project.load(last)

    def _on_tab_changed(self, index: int) -> None:
        self._main_window.tab_by_index(index).activated()

    def build_main_window(self) -> OdcMainWindow:
        return OdcMainWindow()

    def configure_preferences(self) -> None:
        PreferencesService.add_prefs(
            PrefSection(
                "Application",
                "app",
                [
                    PrefGroup(
                        "General",
                        "gen",
                        [
                            PrefItem.new("Open Last Project On Startup", "open-last-proj", True),
                        ],
                    ),
                    PrefGroup(
                        "Connections",
                        "conn",
                        [
                            PrefItem.new("Auto Select Last Device", "sel-last-device", True),
                            PrefItem.new("Auto Connect Last Device", "conn-last-device", False),
                        ],
                    ),
                    PrefGroup(
                        "Arduino",
                        "arduino",
                        [
                            PrefItem.new(
                                "Arduino CLI Path",
                                "cli-path",
                                Path(),
                                widget_class=PathWithPlaceholder(
                                    placeholder_text="bundled arduino-cli",
                                ),
                            ),
                            PrefItem.new("Auto Connect Last Device", "conn-last-device", False),
                        ],
                    ),
                ],
            ),
        )

    def _project_loaded(self, name: str) -> None:
        self._main_window.setWindowTitle(name)
        self._main_window.statusBar().showMessage(f"Loaded: {name}", 3000)
        self._update_save_action_state()

    def _project_saved(self, name: str) -> None:
        self._main_window.setWindowTitle(name)
        self._main_window.statusBar().showMessage(f"Saved: {name}", 3000)
        self._update_save_action_state()
        clear_cursor()

    def _update_save_action_state(self) -> None:
        _save_action: QAction = self._main_window.tool_bar.get_action("Save")
        _save_action.setDisabled(self._project.file_path is None)
