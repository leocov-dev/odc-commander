from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from pyside_app_core import log

from odc_commander.controllers import CalibrationOutput
from odc_commander.interfaces.controller import ControllerView


class CalibrationOutputView(ControllerView[CalibrationOutput]):
    TAB_NAME = "Calibration - Specify Output"

    def __init__(self, controller: CalibrationOutput, parent: QWidget | None = None):
        super().__init__(controller, parent=parent)

        _ly = QVBoxLayout()
        self.setLayout(_ly)

        # ------
        self._graph = QGraphicsView(parent=self)
        _ly.addWidget(self._graph)

        self._graph_scene = QGraphicsScene(parent=self)
        self._graph.setScene(self._graph_scene)

        # ------
        _ly_avg = QHBoxLayout()
        _ly.addLayout(_ly_avg)

        _ly_avg.addWidget(QLabel("1 sec Avg"), alignment=Qt.AlignmentFlag.AlignRight, stretch=2)

        self._avg = QLineEdit(parent=self)
        _ly_avg.addWidget(self._avg, stretch=2)

        self._avg.setReadOnly(True)

        # ------
        self._val = QSpinBox(parent=self)
        _ly.addWidget(self._val)

        self._val.setRange(0, 4095)
        self._val.setSingleStep(8)
        self._val.setValue(2048)

        # ------
        self._slider = QSlider(parent=self)
        _ly.addWidget(self._slider)

        self._slider.setRange(0, 4095)
        self._slider.setSingleStep(8)
        self._slider.setValue(2048)
        self._slider.setOrientation(Qt.Orientation.Horizontal)

        # signals ----
        self._val.editingFinished.connect(lambda: self._slider.setValue(self._val.value()))
        self._val.editingFinished.connect(lambda: self._editing_completed(self._val.value()))
        self._slider.valueChanged.connect(self._val.setValue)
        self._slider.valueChanged.connect(self._editing_completed)

    def _editing_completed(self, val: int) -> None:
        log.debug(val)
