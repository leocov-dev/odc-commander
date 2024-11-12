from PySide6.QtCore import Signal
from pyside_app_core.services.serial_service.types import Encodable

from odc_commander.interfaces.controller import SwitchedController
from odc_commander.interfaces.project.v1 import InputCalibrationComponentData


class CalibrationInput(SwitchedController[Encodable]):
    """"""

    unsaved_changes = Signal()

    component_type = "calibration_input"

    def serialize(self) -> InputCalibrationComponentData:
        return InputCalibrationComponentData(
            component_type=self.component_type,
        )

    def deserialize(self, data: InputCalibrationComponentData) -> None:
        pass

    def restore_defaults(self) -> None:
        pass
