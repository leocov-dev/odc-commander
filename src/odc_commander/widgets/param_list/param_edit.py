from pyside_app_core import log

from odc_commander.commands.basic_params import FloatParam
from odc_commander.widgets.param_list.param_delegate import ParamDelegate
from odc_commander.widgets.param_list.param_widget import ParamWidget
from PySide6.QtCore import QPersistentModelIndex, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)
from pyside_app_core.validators.float_validator import FloatValidator


class ParamEditDialog(QDialog):
    @property
    def index(self) -> QPersistentModelIndex:
        return self._index

    @property
    def param(self) -> FloatParam:
        return FloatParam(
            value=self.default,
            default=self.default,
            label=self.label,
            unit=self.unit,
            step=self.step,
            min_value=self.minimum,
            max_value=self.maximum,
            decimals=self.decimals,
        )

    @property
    def default(self) -> float:
        return float(self._default.text() or 1000.0)

    @property
    def label(self) -> str:
        return self._label.text()

    @property
    def unit(self) -> str:
        return self._unit.text().strip()

    @property
    def step(self) -> float:
        return float(self._step.text() or 0.1)

    @property
    def decimals(self) -> int:
        return self._decimals.value()

    @property
    def minimum(self) -> float:
        return float(self._minimum.text() or 0.0)

    @property
    def maximum(self) -> float:
        return float(self._maximum.text() or self.default * 2)

    @property
    def marked_for_deletion(self) -> bool:
        return self._marked_for_deletion

    def __init__(self, index: QPersistentModelIndex):
        super().__init__(parent=None)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setModal(True)
        self.setFixedWidth(350)

        self._index = index
        _input = ParamDelegate.from_index(index)
        log.debug(f"Edit Param: {_input}")

        self._marked_for_deletion = False

        ly = QVBoxLayout()
        self.setLayout(ly)

        ly_form = QFormLayout()
        ly.addLayout(ly_form)

        self._label = QLineEdit(parent=self)
        self._label.setPlaceholderText("Name Required")
        self._label.setText(_input.label)
        ly_form.addRow("Name", self._label)

        self._default = QLineEdit(parent=self)
        self._default.setText(str(_input.default))
        self._default.setValidator(FloatValidator(self))
        self._default.setAlignment(Qt.AlignmentFlag.AlignRight)
        ly_form.addRow("Default Value", self._default)

        self._maximum = QLineEdit(parent=self)
        self._maximum.setText(str(_input.max_value))
        self._maximum.setValidator(FloatValidator(self))
        self._maximum.setAlignment(Qt.AlignmentFlag.AlignRight)
        ly_form.addRow("Maximum Value", self._maximum)

        self._minimum = QLineEdit(parent=self)
        self._minimum.setText(str(_input.min_value))
        self._minimum.setValidator(FloatValidator(self))
        self._minimum.setAlignment(Qt.AlignmentFlag.AlignRight)
        ly_form.addRow("Minimum Value", self._minimum)

        self._step = QLineEdit(parent=self)
        self._step.setToolTip("Amount value changes for each scroll wheel tick")
        self._step.setValidator(FloatValidator(self))
        self._step.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._step.setText(str(_input.step))
        ly_form.addRow("Step", self._step)

        self._decimals = QSpinBox(parent=self)
        self._decimals.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._decimals.setRange(0, 6)
        self._decimals.setValue(_input.decimals)
        ly_form.addRow("Decimal Places", self._decimals)

        self._unit = QLineEdit(parent=self)
        self._unit.setText(_input.unit)
        ly_form.addRow("Unit Suffix", self._unit)

        ly.addSpacing(10)

        example_group = QGroupBox("Interactive Preview:", self)
        example_group.setLayout(QVBoxLayout())
        ly.addWidget(example_group)

        self._example = ParamWidget(parent=self)
        example_group.layout().addWidget(self._example)

        ly.addSpacing(10)

        ly_btn = QHBoxLayout()
        ly.addLayout(ly_btn)

        cancel = QPushButton("Cancel", parent=self)
        ly_btn.addWidget(cancel, stretch=2)

        delete = QPushButton("Delete", parent=self)
        ly_btn.addWidget(delete, stretch=2)

        self._accept = QPushButton("Accept Changes", parent=self)
        ly_btn.addWidget(self._accept, stretch=2)

        # ---

        cancel.clicked.connect(lambda: self.done(QDialog.DialogCode.Rejected))
        delete.clicked.connect(self._mark)
        self._accept.clicked.connect(lambda: self.done(QDialog.DialogCode.Accepted))

        self._reset_example()

        for sig in [
            self._label.textChanged,
            self._default.textChanged,
            self._step.textChanged,
            self._unit.textChanged,
            self._minimum.textChanged,
            self._maximum.textChanged,
            self._decimals.valueChanged,
        ]:
            sig.connect(self._reset_example)

    def _reset_example(self) -> None:
        self._example.set_values(
            value=self.default,
            label=self.label,
            decimals=self.decimals,
            single_step=self.step,
            suffix=f" {self.unit}",
            minimum=self.minimum,
            maximum=self.maximum,
            default=self.default,
        )

        self._minimum.setPlaceholderText(f"default: {self.minimum}")
        self._maximum.setPlaceholderText(f"default: {self.maximum}")
        self._step.setPlaceholderText(f"default: {self.step}")

        self._validate()

    def _validate(self) -> None:
        valid = all(
            [
                bool(self._label.text()),
                self.step > 0,
            ]
        )
        self._accept.setEnabled(valid)

    def _mark(self) -> None:
        self._marked_for_deletion = True
        self.done(QDialog.DialogCode.Accepted)
