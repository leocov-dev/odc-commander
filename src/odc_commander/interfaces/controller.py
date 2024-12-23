from typing import Generic, NamedTuple, TypeVar

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from PySide6.QtWidgets import QWidget
from pyside_app_core import log
from pyside_app_core.services.serial_service import SerialService
from pyside_app_core.services.serial_service.types import Encodable, TranscoderInterface
from pyside_app_core.utils.signals import OneToManySwitcher

_D = TypeVar("_D", bound=Encodable)


class SerialConfig(NamedTuple):
    com: SerialService
    com_data: OneToManySwitcher


class Controller(QObject, Generic[_D]):
    connected = Signal(QSerialPort)
    disconnected = Signal()

    def __init__(
        self,
        serial_config: SerialConfig,
        *,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)

        self._serial = serial_config

    @property
    def serial_com(self) -> SerialService:
        return self._serial.com

    def send(self, value: _D) -> None:
        self.serial_com.send_data(value)

    @Slot()
    def handle_serial_connect(self, com: QSerialPort) -> None:
        log.debug(f"<{self.__class__.__name__}> connected to serial port {com.portName()}")
        self.connected.emit(com)

    @Slot()
    def handle_serial_disconnect(self) -> None:
        log.debug(f"<{self.__class__.__name__}> disconnected")
        self.disconnected.emit()

    @Slot()
    def handle_serial_data(self, data: object) -> None:
        log.debug(f"<{self.__class__.__name__}> received data: {data}")

    @Slot()
    def handle_serial_error(self, error: Exception) -> None:
        log.debug(f"<{self.__class__.__name__}> received error: {error}")

    @Slot()
    def handle_serial_ports(self, ports: list[QSerialPortInfo]) -> None:
        # ignored
        pass


class SwitchedController(Controller[_D]):
    @property
    def switch_index(self) -> int:
        return self._switch_index

    def __init__(
        self,
        serial_config: SerialConfig,
        transcoder: type[TranscoderInterface],
        *,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(serial_config, parent=parent)

        self._transcoder: type[TranscoderInterface] = transcoder

        self.serial_com.com_connect.connect(self.handle_serial_connect)
        self.serial_com.com_disconnect.connect(self.handle_serial_disconnect)
        self.serial_com.com_ports.connect(self.handle_serial_ports)
        self.serial_com.com_error.connect(self.handle_serial_error)

        self._switch_index = self._serial.com_data.connect_switched(self.handle_serial_data)

    def activated(self) -> None:
        self.serial_com.set_transcoder(self._transcoder)


CC = TypeVar("CC", bound=Controller[Encodable])


class ControllerView(QWidget, Generic[CC]):
    TAB_NAME: str = ""

    def __init__(
        self,
        controller: CC,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)

        self._controller: CC = controller

    @property
    def controller(self) -> CC:
        return self._controller
