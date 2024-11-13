from collections.abc import Sequence
from enum import IntEnum
from typing import Self

from PySide6.QtCore import QModelIndex, QObject, QPersistentModelIndex
from PySide6.QtGui import QStandardItem, QStandardItemModel, Qt

from odc_commander.commands.basic_params import FloatArrayParam, FloatParam


class ParamData(IntEnum):
    LABEL = Qt.ItemDataRole.DisplayRole
    VALUE = Qt.ItemDataRole.UserRole + 1
    UNIT = Qt.ItemDataRole.UserRole + 2
    MIN = Qt.ItemDataRole.UserRole + 3
    MAX = Qt.ItemDataRole.UserRole + 4
    STEP = Qt.ItemDataRole.UserRole + 5
    DEFAULT = Qt.ItemDataRole.UserRole + 6
    DECIMALS = Qt.ItemDataRole.UserRole + 7
    TOOLTIP = Qt.ItemDataRole.ToolTipRole


def _param_to_std_item(param: FloatParam) -> QStandardItem:
    item = QStandardItem()
    item.setDragEnabled(True)
    item.setDropEnabled(False)

    item.setData(param.label, ParamData.LABEL)
    item.setData(param.value, ParamData.VALUE)
    item.setData(param.unit, ParamData.UNIT)
    item.setData(param.min_value, ParamData.MIN)
    item.setData(param.max_value, ParamData.MAX)
    item.setData(param.step, ParamData.STEP)
    item.setData(param.default, ParamData.DEFAULT)
    item.setData(param.decimals, ParamData.DECIMALS)
    return item


class ParamModel(QStandardItemModel):
    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.MoveAction

    @classmethod
    def from_param_list(cls, data: Sequence[FloatParam], *, parent: QObject) -> Self:
        model = cls(parent=parent)

        for param in data:
            model.add_param(param)

        return model

    def add_param(self, param: FloatParam) -> None:
        self.appendRow(_param_to_std_item(param))

    def set_all_data(self, index: QModelIndex | QPersistentModelIndex, param: FloatParam) -> None:
        self.setData(index, param.label, ParamData.LABEL)
        self.setData(index, param.value, ParamData.VALUE)
        self.setData(index, param.unit, ParamData.UNIT)
        self.setData(index, param.min_value, ParamData.MIN)
        self.setData(index, param.max_value, ParamData.MAX)
        self.setData(index, param.step, ParamData.STEP)
        self.setData(index, param.default, ParamData.DEFAULT)
        self.setData(index, param.decimals, ParamData.DECIMALS)

    def to_float_array_param(self) -> FloatArrayParam:
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
                    default=item.data(ParamData.DEFAULT),
                    decimals=item.data(ParamData.DECIMALS),
                )
            )

        return FloatArrayParam(*params)
