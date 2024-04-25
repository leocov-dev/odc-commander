import logging

from odc_commander import commands, controllers
from odc_commander.widgets.controller_views.calibration_input_view import CalibrationInputView
from odc_commander.widgets.controller_views.calibration_output_view import CalibrationOutputView
from odc_commander.widgets.controller_views.runtime_view import RuntimeView
from odc_commander.widgets.main_window import OdcMainWindow
from PySide6.QtSerialPort import QSerialPortInfo
from pyside_app_core.qt.widgets.base_app import BaseApp
from pyside_app_core.services.serial_service import SerialService

logging.basicConfig(level=logging.DEBUG)


def _port_filter(ports: list[QSerialPortInfo]) -> list[QSerialPortInfo]:
    filtered = []

    for port in ports:
        if "bluetooth" in port.portName().lower():
            continue

    return filtered


class OdcCommanderApp(BaseApp):
    """ Main App """

    def __init__(self):
        super(OdcCommanderApp, self).__init__(resources_rcc=None)

        self._main_window = OdcMainWindow()

        self._serial_com = SerialService(commands.LegacyTranscoder, parent=self)
        self._serial_com.set_port_filter(_port_filter)

        self._serial_com.register_reader(self._main_window._connection_manager)

        self._main_window.add_controller_view(RuntimeView(controllers.Runtime()))
        self._main_window.add_controller_view(CalibrationInputView(controllers.CalibrationInput()))
        self._main_window.add_controller_view(CalibrationOutputView(controllers.CalibrationOutput()))
