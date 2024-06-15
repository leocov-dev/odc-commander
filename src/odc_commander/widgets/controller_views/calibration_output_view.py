from PySide6.QtWidgets import QWidget

from odc_commander.interfaces.controller import ControllerView


class CalibrationOutputView(ControllerView):
    TAB_NAME = "Output Calibration"

    def __init__(self, controller: object, parent: QWidget | None = None):  # noqa: ARG002
        super().__init__(parent=parent)
