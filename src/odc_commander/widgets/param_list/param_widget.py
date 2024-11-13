from typing import cast

from odc_commander.commands.basic_params import FloatParam
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QSizePolicy, QWidget


class ParamWidget(QWidget):
    value_changed = Signal(float)

    @property
    def param(self) -> FloatParam:
        return FloatParam(
            value=self._spin_box.value(),
            default=self._default,
            label=self._label.text(),
            unit=self._spin_box.suffix().strip(),
            step=self._spin_box.singleStep(),
            min_value=self._spin_box.minimum(),
            max_value=self._spin_box.maximum(),
            decimals=self._spin_box.decimals(),
        )

    def __init__(
        self,
        param: FloatParam | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self.setAutoFillBackground(True)

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._default = 0.0

        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.layout().addWidget(self._label, stretch=1)

        self.layout().addSpacing(0)

        self._spin_box = QDoubleSpinBox(parent=self)
        self._spin_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._spin_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout().addWidget(self._spin_box, stretch=1)

        if param:
            self.set_from_param(param)

        self._spin_box.valueChanged.connect(self.value_changed)

    def layout(self) -> QHBoxLayout:
        return cast(QHBoxLayout, super().layout())

    def set_values(
        self,
        *,
        value: float,
        label: str,
        decimals: int,
        single_step: float,
        suffix: str,
        minimum: float,
        maximum: float,
        default: float,
    ) -> None:
        self._label.setText(label)
        self._spin_box.setDecimals(decimals)
        self._spin_box.setSingleStep(single_step)
        self._spin_box.setSuffix(f" {suffix}")
        self._spin_box.setRange(minimum, maximum)
        self._spin_box.setValue(value or default)

        self._default = default

    def set_from_param(self, param: FloatParam) -> None:
        self.set_values(
            value=param.value,
            label=param.label,
            decimals=param.decimals,
            single_step=param.step,
            suffix=param.unit,
            minimum=param.min_value,
            maximum=param.max_value,
            default=param.default,
        )
