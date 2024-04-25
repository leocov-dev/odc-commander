from PySide6 import QtWidgets


class CalibrationOutputView(QtWidgets.QWidget):
    def __init__(self, controller, parent: QtWidgets.QWidget | None = None):
        super(CalibrationOutputView, self).__init__(parent=parent)
