from PySide6 import QtWidgets


class CalibrationInputView(QtWidgets.QWidget):
    def __init__(self, controller, parent: QtWidgets.QWidget | None = None):
        super(CalibrationInputView, self).__init__(parent=parent)
