from PySide6 import QtWidgets


class RuntimeView(QtWidgets.QWidget):
    def __init__(self, controller: object, parent: QtWidgets.QWidget | None = None) -> None:
        super(RuntimeView, self).__init__(parent=parent)