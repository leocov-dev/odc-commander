import logging

from PySide6.QtSerialPort import QSerialPortInfo
from PySide6.QtWidgets import QMainWindow
from pyside_app_core.qt.standard import MainWindow
from pyside_app_core.qt.widgets.base_app import BaseApp
from pyside_app_core.services.serial_service import SerialService

from odc_commander import commands, controllers
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


class OdcCommanderApp(BaseApp):
    """ Main App """

    def __init__(self) -> None:
        super(OdcCommanderApp, self).__init__(resources_rcc=None)

        self._main_window = OdcMainWindow()

        self._serial_com = SerialService(commands.LegacyTranscoder, parent=self)
        self._serial_com.set_port_filter(_port_filter)

        self._main_window.connection_manager.refresh_ports.connect(self._serial_com.scan_for_ports)
        self._main_window.connection_manager.request_connect.connect(self._serial_com.open_connection)
        self._main_window.connection_manager.request_disconnect.connect(self._serial_com.close_connection)
        self._serial_com.register_reader(self._main_window.connection_manager)

        self._main_window.add_controller_view(RuntimeView(controllers.Runtime()))
        self._main_window.add_controller_view(CalibrationInputView(controllers.CalibrationInput()))
        self._main_window.add_controller_view(CalibrationOutputView(controllers.CalibrationOutput()))

    def build_main_window(self) -> QMainWindow:
        return MainWindow()
