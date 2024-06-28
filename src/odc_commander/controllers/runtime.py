from PySide6.QtCore import QObject

from odc_commander.commands.basic_params import FloatArrayParam, FloatParam
from odc_commander.widgets.param_list.param_model import ParamModel


class Runtime(QObject):
    """"""

    def __init__(self, params: FloatArrayParam, parent: QObject):
        super().__init__(parent=parent)

        self._model = ParamModel.from_param_list(params.params, parent=self)

    @property
    def params(self) -> list[FloatParam]:
        return self._model.to_float_array_param("Runtime").params

    @property
    def model(self) -> ParamModel:
        return self._model
