from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from pyside_app_core import log
from pyside_app_core.services.serial_service.types import Encodable


class CalibrationOutput(QObject):
    """"""

    send_value = Signal(Encodable)

    @Slot()
    def handle_serial_connect(self, com: QSerialPort) -> None:
        log.debug(f"Connected to serial port {com.portName()}")

    @Slot()
    def handle_serial_disconnect(self) -> None:
        log.debug("Com port disconnected")

    @Slot()
    def handle_serial_data(self, data: object) -> None:
        log.debug(f"Received data: {data}")

    @Slot()
    def handle_serial_error(self, error: Exception) -> None:
        log.debug(f"Error received: {error}")

    @Slot()
    def handle_serial_ports(self, ports: list[QSerialPortInfo]) -> None:
        # ignored
        pass
