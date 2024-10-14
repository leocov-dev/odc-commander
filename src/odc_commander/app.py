from pathlib import Path

from loguru import logger
from PySide6.QtSerialPort import QSerialPortInfo
from pyside_app_core.app.application_service import AppMetadata
from pyside_app_core.errors import excepthook
from pyside_app_core.log import configure_get_logger_func
from pyside_app_core.services.preferences_service import PreferencesService, PrefGroup, PrefItem, PrefSection
from pyside_app_core.services.serial_service import SerialService
from pyside_app_core.ui.prefs import PathWithPlaceholder
from pyside_app_core.ui.prefs.preferences_utility_widgets import ComboItemWidget
from pyside_app_core.ui.standard.error_dialog import ErrorDialog
from pyside_app_core.ui.widgets.base_app import BaseApp
from pyside_app_core.utils.signals import OneToManySwitcher

from odc_commander import __version__, commands, controllers, DATA_DIR
from odc_commander.arduino.sketch import get_sketch
from odc_commander.arduino.vendor_map import VENDOR_MAP
from odc_commander.interfaces.controller import SerialConfig
from odc_commander.parameters import RUNTIME_PARAMS
from odc_commander.widgets.controller_views.calibration_input_view import CalibrationInputView
from odc_commander.widgets.controller_views.calibration_output_view import CalibrationOutputView
from odc_commander.widgets.controller_views.runtime_view import RuntimeView
from odc_commander.widgets.main_window import OdcMainWindow

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
    oss_licenses=[
        ":/odc/licenses/arduino-cli.md"
    ],
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

    def __init__(self) -> None:
        super().__init__(resources_rcc=DATA_DIR / "resources.rcc")

        PreferencesService.add_prefs(
            PrefSection(
                "Application",
                "app",
                [
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
            PrefGroup(
                "Developer",
                "dev",
                [
                    PrefItem.new("Debug Mode", "debug", False),
                    PrefItem.new(
                        "Log Level",
                        "log-level",
                        2,
                        widget_class=ComboItemWidget(["ERROR", "WARNING", "INFO", "DEBUG"]),
                    ),
                ],
            ),
        )

        # ---
        # serial service
        self._serial_com = SerialService(commands.LegacyTranscoder, parent=self)
        self._serial_com.set_port_filter(_port_filter)

        self._main_window.set_serial_service(self._serial_com)

        # ----
        _sw_data = OneToManySwitcher(self._serial_com.com_data, parent=self)
        _serial_config = SerialConfig(self._serial_com, _sw_data)

        # ---
        # controllers
        self._runtime_controller = controllers.Runtime(
            _serial_config,
            RUNTIME_PARAMS,
            parent=self,
        )
        self._runtime_controller.as_partial_reader()
        self._runtime_view = RuntimeView(self._runtime_controller)
        # ---
        self._calibration_input_controller = controllers.CalibrationInput(
            _serial_config,
            parent=self,
        )
        self._calibration_input_controller.as_partial_reader()
        self._calibration_input_view = CalibrationInputView(self._calibration_input_controller)
        # ---
        self._calibration_output_controller = controllers.CalibrationOutput(
            _serial_config,
            parent=self,
        )
        self._calibration_output_controller.as_partial_reader()
        self._calibration_output_view = CalibrationOutputView(self._calibration_output_controller)

        # ---
        # tab views
        self._main_window.add_controller_tab(
            self._runtime_view,
            None,
            "Upload Firmware",
            readonly=False,
        )
        self._main_window.add_controller_tab(
            self._calibration_input_view,
            get_sketch("calibration-input-output"),
            "Upload Calibration Firmware",
            readonly=True,
        )
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
        # connection management
        self._main_window.connection_manager.refresh_ports.connect(self._serial_com.scan_for_ports)
        self._main_window.connection_manager.request_connect.connect(self._serial_com.open_connection)
        self._main_window.connection_manager.request_disconnect.connect(self._serial_com.close_connection)
        # debug
        SerialService.DEBUG = False

        def _change_debug_mode(debug: bool) -> None:
            SerialService.DEBUG = debug

        self._main_window.debug_mode.connect(_change_debug_mode)

    def build_main_window(self) -> OdcMainWindow:
        return OdcMainWindow()
