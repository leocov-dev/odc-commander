import logging

from PySide6.QtSerialPort import QSerialPortInfo
from pyside_app_core.qt.widgets.base_app import BaseApp
from pyside_app_core.services.serial_service import SerialService

from odc_commander import commands, controllers
from odc_commander.parameters import RUNTIME_PARAMS
from odc_commander.widgets.controller_views.calibration_input_view import CalibrationInputView
from odc_commander.widgets.controller_views.calibration_output_view import CalibrationOutputView
from odc_commander.widgets.controller_views.runtime_view import RuntimeView
from odc_commander.widgets.main_window import OdcMainWindow

logging.basicConfig(level=logging.DEBUG)


def _port_filter(ports: list[QSerialPortInfo]) -> list[QSerialPortInfo]:
    filtered = []

    port_names = [p.portName() for p in ports]

    for port in ports:
        if "bluetooth" in port.portName().lower():
            continue
        if port.portName().startswith("tty.") and port.portName().replace("tty.", "cu.") in port_names:
            continue

        filtered.append(port)

    return filtered


class OdcCommanderApp(BaseApp[OdcMainWindow]):
    """Main App"""

    def __init__(self) -> None:
        super().__init__()

        # ---
        # serial service
        self._serial_com = SerialService(commands.LegacyTranscoder, parent=self)
        self._serial_com.set_port_filter(_port_filter)

        # ---
        # controllers
        self._runtime_controller = controllers.Runtime(RUNTIME_PARAMS, parent=self)
        self._calibration_input_controller = controllers.CalibrationInput(parent=self)
        self._calibration_output_controller = controllers.CalibrationOutput(parent=self)

        # ---
        # tab views
        self._main_window.add_controller_tab(RuntimeView(self._runtime_controller))
        self._main_window.add_controller_tab(CalibrationInputView(self._calibration_input_controller))
        self._main_window.add_controller_tab(CalibrationOutputView(self._calibration_output_controller))

        # ---
        # serial data readers
        self._serial_com.register_reader(self._main_window.connection_manager)
        self._serial_com.register_reader(self._runtime_controller)
        self._serial_com.register_reader(self._calibration_input_controller)
        self._serial_com.register_reader(self._calibration_output_controller)

        # ---
        # connection management
        self._main_window.connection_manager.refresh_ports.connect(self._serial_com.scan_for_ports)
        self._main_window.connection_manager.request_connect.connect(self._serial_com.open_connection)
        self._main_window.connection_manager.request_disconnect.connect(self._serial_com.close_connection)

        # ---
        # sending data
        self._runtime_controller.send_parameters.connect(self._serial_com.send_data)
        self._calibration_input_controller.send_command.connect(self._serial_com.send_data)
        self._calibration_output_controller.send_value.connect(self._serial_com.send_data)

    def build_main_window(self) -> OdcMainWindow:
        return OdcMainWindow()
