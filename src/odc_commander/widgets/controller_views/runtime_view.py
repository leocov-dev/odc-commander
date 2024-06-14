from PySide6.QtGui import QUndoCommand
from PySide6.QtWidgets import QDoubleSpinBox, QFormLayout, QLayout, QSizePolicy, QVBoxLayout, QWidget

from odc_commander.controllers import Runtime


class ParamCommand(QUndoCommand):
    def __init__(self, param_control: QWidget, parent: QUndoCommand | None = None):
        super().__init__(parent=parent)
        self._param_control = param_control


class RuntimeView(QWidget):
    def __init__(self, controller: Runtime, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self._controller = controller
        # self.setMinimumHeight(500)

        # _contents = QWidget(self)
        # self.setWidget(_contents)
        # self.setWidgetResizable(False)
        # self.setBackgroundRole(QPalette.ColorRole.Mid)

        _ly = QVBoxLayout()
        _ly.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        _ly.setContentsMargins(30, 30, 30, 30)
        self.setLayout(_ly)

        self._form = QFormLayout()
        _ly.addLayout(self._form)

        for param in self._controller.params:
            spin = QDoubleSpinBox(parent=self)
            spin.setSizePolicy(
                QSizePolicy.Policy.MinimumExpanding,
                QSizePolicy.Policy.Minimum,
            )

            spin.setValue(param.value)
            spin.setSingleStep(param.step)
            spin.setRange(param.min_value * 10, param.max_value * 10)
            spin.setSuffix(param.unit)
            # spin.valueChanged.connect(lambda v: param.value = v)

            self._form.addRow(param.label, spin)

        # self.adjustSize()
