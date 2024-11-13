from typing import cast

from PySide6.QtCore import QPersistentModelIndex, QPoint
from PySide6.QtGui import QUndoCommand
from PySide6.QtWidgets import QHBoxLayout, QLayout, QMessageBox, QPushButton, QVBoxLayout, QWidget

from odc_commander.controllers import Runtime
from odc_commander.interfaces.controller import ControllerView
from odc_commander.widgets.param_list.param_create import ParamCreateDialog
from odc_commander.widgets.param_list.param_edit import ParamEditDialog
from odc_commander.widgets.param_list.param_view import ParamView


class ParamCommand(QUndoCommand):
    def __init__(self, param_control: QWidget, parent: QUndoCommand | None = None):
        super().__init__(parent=parent)
        self._param_control = param_control


class RuntimeView(ControllerView[Runtime]):
    TAB_NAME = "Runtime Control"

    def __init__(self, controller: Runtime, parent: QWidget | None = None) -> None:
        super().__init__(controller=controller, parent=parent)

        _ly = QVBoxLayout()
        _ly.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        _ly.setContentsMargins(10, 10, 10, 10)
        self.setLayout(_ly)

        self._view = ParamView(parent=self)
        _ly.addWidget(self._view)

        _ly_create = QHBoxLayout()
        _ly.addLayout(_ly_create)

        _clear = QPushButton("Clear All")
        _ly_create.addWidget(_clear, stretch=1)
        _create = QPushButton("Add Parameter")
        _ly_create.addWidget(_create, stretch=1)

        _ly_create.addStretch(2)

        _send = QPushButton("Commit All Parameters")
        _send.setDisabled(True)
        _ly_create.addWidget(_send, stretch=2)

        # ---

        self._view.setModel(self._controller.model)
        self._view.edit_index_requested.connect(self._edit_index)

        _clear.clicked.connect(self._confirm_clear)
        _create.clicked.connect(self._show_create_dialog)
        _send.clicked.connect(lambda: self.controller.send_all_params())
        self.controller.disconnected.connect(lambda: _send.setDisabled(True))
        self.controller.connected.connect(lambda *_: _send.setEnabled(True))
        self.controller.param_validation.connect(_send.setEnabled)

    def _show_create_dialog(self) -> None:
        create = ParamCreateDialog()
        create.accepted.connect(self._create_accepted)

        create.show()

    def _create_accepted(self) -> None:
        param = cast(ParamCreateDialog, self.sender()).param

        self._controller.add_param(param)

    def _confirm_clear(self) -> None:
        res = QMessageBox.question(  # type: ignore[call-overload]
            None,
            "Clear All Parameters",
            "Are you sure you want to clear all parameters?",
            defaultButton=QMessageBox.StandardButton.No,
        )

        if res == QMessageBox.StandardButton.Yes:
            self._view.model().clear()

    def _edit_index(self, index: QPersistentModelIndex) -> None:
        edit = ParamEditDialog(index)
        edit.accepted.connect(self._edit_accepted)

        edit.show()

    def _edit_accepted(self) -> None:
        dia = cast(ParamEditDialog, self.sender())

        self._view.update_delegate_mouse_pos(QPoint(0, 0))

        if dia.marked_for_deletion:
            self.controller.remove_row(dia.index.row())
        else:
            self.controller.set_row_data(dia.index.row(), dia.param)
            self._view.repaint_index(dia.index)
