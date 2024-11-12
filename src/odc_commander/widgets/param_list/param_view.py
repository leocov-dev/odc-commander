from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QPoint, Qt, Signal
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QAbstractItemView, QListView, QWidget

from odc_commander.widgets.param_list.param_delegate import ParamDelegate
from odc_commander.widgets.param_list.param_model import ParamData, ParamModel


class ParamView(QListView):
    edit_index_requested = Signal(QPersistentModelIndex)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)

        self.setSpacing(3)
        self.viewport().setBackgroundRole(QPalette.ColorRole.Window)
        self.viewport().setMouseTracking(True)

        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDropIndicatorShown(True)

        self.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.setItemDelegate(ParamDelegate(self))
        self.itemDelegate().open_editor.connect(self.edit)
        self.itemDelegate().reset_index.connect(self._reset_index)
        self.itemDelegate().edit_index.connect(self.edit_index_requested.emit)

    def model(self) -> ParamModel:
        return super().model()  # type: ignore[return-value]

    def itemDelegate(self) -> ParamDelegate:
        return super().itemDelegate()  # type: ignore[return-value]

    def repaint_index(self, index: QModelIndex | QPersistentModelIndex) -> None:
        self.viewport().repaint(self.rectForIndex(index))

    def update_delegate_mouse_pos(self, point: QPoint) -> None:
        self.itemDelegate()._mouse = point

    def _reset_index(self, index: QPersistentModelIndex) -> None:
        default = index.data(ParamData.DEFAULT)
        self.model().setData(index, default, ParamData.VALUE)
