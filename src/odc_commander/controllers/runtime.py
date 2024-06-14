from odc_commander.commands.basic_params import FloatArrayParam, FloatParam


class Runtime:
    """"""

    def __init__(self, params: FloatArrayParam):
        self._param_array = params

    @property
    def params(self) -> list[FloatParam]:
        return self._param_array.params
