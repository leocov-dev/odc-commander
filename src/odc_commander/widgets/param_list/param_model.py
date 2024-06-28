from enum import IntEnum
from typing import Self

from PySide6.QtCore import QObject
from PySide6.QtGui import QStandardItem, QStandardItemModel, Qt

from odc_commander.commands.basic_params import FloatArrayParam, FloatParam


class ParamData(IntEnum):
    VALUE = Qt.ItemDataRole.UserRole + 1
    UNIT = Qt.ItemDataRole.UserRole + 2
    MIN = Qt.ItemDataRole.UserRole + 3
    MAX = Qt.ItemDataRole.UserRole + 4
    STEP = Qt.ItemDataRole.UserRole + 5


def _param_to_std_item(param: FloatParam) -> QStandardItem:
    item = QStandardItem(param.label)
    item.setData(param.value, ParamData.VALUE)
    item.setData(param.unit, ParamData.UNIT)
    item.setData(param.min_value, ParamData.MIN)
    item.setData(param.max_value, ParamData.MAX)
    item.setData(param.step, ParamData.STEP)
    return item


class ParamModel(QStandardItemModel):
    @classmethod
    def from_param_list(cls, data: list[FloatParam], *, parent: QObject) -> Self:
        model = cls(parent=parent)

        for param in data:
            model.appendRow(_param_to_std_item(param))

        return model

    def add_param(self, param: FloatParam) -> None:
        self.appendRow(_param_to_std_item(param))

    def to_float_array_param(self, name: str) -> FloatArrayParam:
        params = []
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            params.append(
                FloatParam(
                    label=item.text(),
                    value=item.data(ParamData.VALUE),
                    unit=item.data(ParamData.UNIT),
                    min_value=item.data(ParamData.MIN),
                    max_value=item.data(ParamData.MAX),
                    step=item.data(ParamData.STEP),
                )
            )

        return FloatArrayParam(name, *params)
