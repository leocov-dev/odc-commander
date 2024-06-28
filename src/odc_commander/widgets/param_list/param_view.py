from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QListView, QWidget

from odc_commander.widgets.param_list.param_model import ParamModel


class ParamView(QListView):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)

        self.setSpacing(3)
        self.viewport().setBackgroundRole(QPalette.ColorRole.Window)

    def setModel(self, model: ParamModel) -> None:  # type: ignore[override]
        super().setModel(model)

    def model(self) -> ParamModel:
        return super().model()  # type: ignore[return-value]
