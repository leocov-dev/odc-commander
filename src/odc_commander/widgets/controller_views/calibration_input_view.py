from PySide6.QtWidgets import QWidget

from odc_commander.interfaces.controller import ControllerView


class CalibrationInputView(ControllerView):
    TAB_NAME = "Input Calibration"

    def __init__(self, controller: object, parent: QWidget | None = None):  # noqa: ARG002
        super().__init__(parent=parent)
