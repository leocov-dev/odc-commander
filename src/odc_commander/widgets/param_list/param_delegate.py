from PySide6.QtCore import QModelIndex, QPersistentModelIndex
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QWidget


class ParamDelegate(QStyledItemDelegate):
    """"""

    def createEditor(
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,  # noqa: ARG002
        index: QModelIndex | QPersistentModelIndex,  # noqa: ARG002
    ) -> QWidget:
        """"""
        return QWidget(parent=parent)
