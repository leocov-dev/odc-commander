from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from pyside_app_core import log
from pyside_app_core.services.serial_service.types import Encodable

from odc_commander.commands.basic_params import FloatArrayParam, FloatParam
from odc_commander.widgets.param_list.param_model import ParamModel


class Runtime(QObject):
    """"""

    send_parameters = Signal(Encodable)

    def __init__(self, params: FloatArrayParam, *, parent: QObject):
        super().__init__(parent=parent)

        self._model = ParamModel.from_param_list(params.params, parent=self)

    @property
    def params(self) -> list[FloatParam]:
        return self._model.to_float_array_param("Runtime").params

    @property
    def model(self) -> ParamModel:
        return self._model

    # --------------------------------------------------------------------------
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
