from PySide6.QtCore import QObject
from pyside_app_core.services.serial_service.types import Encodable

from odc_commander.commands.basic_params import FloatArrayParam, FloatParam
from odc_commander.interfaces.controller import Controller, SerialConfig
from odc_commander.widgets.param_list.param_model import ParamModel


class Runtime(Controller[Encodable]):
    """"""

    def __init__(self, serial_config: SerialConfig, params: FloatArrayParam, *, parent: QObject):
        super().__init__(serial_config=serial_config, parent=parent)

        self._model = ParamModel.from_param_list(params.params, parent=self)

    @property
    def params(self) -> list[FloatParam]:
        return self._model.to_float_array_param("Runtime").params

    @property
    def model(self) -> ParamModel:
        return self._model
