from PySide6.QtWidgets import QWidget


class CalibrationOutputView(QWidget):
    def __init__(self, controller: object, parent: QWidget | None = None):  # noqa: ARG002
        super().__init__(parent=parent)
