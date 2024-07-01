from PySide6.QtWidgets import QWidget

from odc_commander.controllers import CalibrationInput
from odc_commander.interfaces.controller import ControllerView


class CalibrationInputView(ControllerView[CalibrationInput]):
    TAB_NAME = "Calibration - Model Cell"

    def __init__(self, controller: CalibrationInput, parent: QWidget | None = None):  # noqa: ARG002
        super().__init__(controller=controller, parent=parent)
