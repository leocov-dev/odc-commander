from PySide6 import QtWidgets


class CalibrationOutputView(QtWidgets.QWidget):
    def __init__(self, controller: object, parent: QtWidgets.QWidget | None = None):  # noqa: ARG002
        super().__init__(parent=parent)
