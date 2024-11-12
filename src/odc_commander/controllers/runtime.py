import struct

from PySide6.QtCore import QObject, Signal
from pyside_app_core import log
from pyside_app_core.constants import DATA_STRUCT_ENDIAN
from pyside_app_core.services.serial_service.conversion_utils import int_from_bytes
from pyside_app_core.services.serial_service.types import Encodable, TranscoderInterface

from odc_commander.commands import LegacyTranscoder
from odc_commander.commands.basic_params import FloatParam
from odc_commander.commands.transcoder import FloatResult, Result
from odc_commander.interfaces.controller import SerialConfig, SwitchedController
from odc_commander.interfaces.project.v1 import RuntimeComponentData
from odc_commander.widgets.param_list.param_model import ParamModel


class Runtime(SwitchedController[Encodable]):
    unsaved_changes = Signal()
    param_validation = Signal(bool)

    component_type = "runtime"

    # defaults for standard dynamic_clamp.ino firmware
    _DEFAULTS = [
        FloatParam(label="g_shunt", default=0.0, unit="nS", min_value=0.0, max_value=1000.0),
        FloatParam(label="g_hcn", default=0.0, unit="nS", min_value=0.0, max_value=1000.0),
        FloatParam(label="g_Na", default=0.0, unit="nS", min_value=0.0, max_value=1000.0),
        FloatParam(label="m_OU_exc", default=0.0, unit="nS", min_value=0.0, max_value=1000.0),
        FloatParam(label="D_OU_exc", default=0.0, unit="nS²/msec", min_value=0.0, max_value=1000.0),
        FloatParam(label="m_OU_inh", default=0.0, unit="nS", min_value=0.0, max_value=1000.0),
        FloatParam(label="D_OU_inh", default=0.0, unit="nS²/msec", min_value=0.0, max_value=1000.0),
        FloatParam(label="g_espc", default=0.0, unit="nS", min_value=0.0, max_value=1000.0),
    ]

    def __init__(self, serial_config: SerialConfig, transcoder: type[TranscoderInterface], *, parent: QObject):
        super().__init__(
            serial_config=serial_config,
            transcoder=transcoder,
            parent=parent,
        )

        self._model = ParamModel.from_param_list(self._DEFAULTS, parent=self)

        self._param_validation = []

        # ---
        self._model.dataChanged.connect(lambda *_: self.unsaved_changes.emit())
        self._model.rowsInserted.connect(lambda *_: self.unsaved_changes.emit())
        self._model.rowsRemoved.connect(lambda *_: self.unsaved_changes.emit())
        self._model.layoutChanged.connect(lambda *_: self.unsaved_changes.emit())

    @property
    def params(self) -> list[FloatParam]:
        return self._model.to_float_array_param().params

    @property
    def model(self) -> ParamModel:
        return self._model

    def clear(self) -> None:
        self._model.clear()

    def remove_row(self, row: int) -> None:
        self.model.removeRow(row)

    def set_row_data(self, row: int, params: FloatParam) -> None:
        self.model.set_all_data(self.model.index(row, 0), params)

    def add_param(self, param: FloatParam) -> None:
        self.model.add_param(param)

    def serialize(self) -> RuntimeComponentData:
        return RuntimeComponentData(
            component_type=self.component_type,
            params=self.params,
        )

    def deserialize(self, data: RuntimeComponentData) -> None:
        self.clear()
        for param in data.params:
            self.add_param(param)

    def restore_defaults(self) -> None:
        self.clear()
        for param in self._DEFAULTS:
            self.add_param(param)

    def send_all_params(self) -> None:
        params = self.model.to_float_array_param()
        log.debug(f"Sending params: {params}")
        self.send(params)

    def handle_serial_data(self, data: FloatResult) -> None:
        log.debug(f"<{self.__class__.__name__}> received data: {data}")

        self._param_validation.append(data.value)

        if len(self._param_validation) == len(self.params):
            is_valid = self._param_validation == [p.value for p in self.params]
            log.debug(f"filled validation array: {self._param_validation} - {[p.value for p in self.params]} - {is_valid}")
            self.param_validation.emit(is_valid)
            self._param_validation.clear()



