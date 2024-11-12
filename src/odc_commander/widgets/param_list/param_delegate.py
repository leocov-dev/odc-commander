from typing import cast, NamedTuple

from PySide6.QtCore import QEvent, QMargins, QModelIndex, QPersistentModelIndex, QPoint, QRect, QSize, QTimer, Signal
from PySide6.QtGui import QDragEnterEvent, QIcon, QMouseEvent, QPainter, QPalette, Qt
from PySide6.QtWidgets import (
    QAbstractSpinBox, QApplication,
    QDoubleSpinBox, QStyle,
    QStyledItemDelegate,
    QStyleOptionSpinBox,
    QStyleOptionViewItem,
    QWidget,
)
from pyside_app_core import log
from pyside_app_core.ui.widgets.core_icon import CoreIcon
from pyside_app_core.utils.painter import safe_paint

from odc_commander.commands.basic_params import FloatParam
from odc_commander.widgets.param_list.param_model import ParamData, ParamModel


class SpinBoxRect(NamedTuple):
    opts: QStyleOptionSpinBox
    bounds: QRect
    text: QRect


class Rects(NamedTuple):
    drag: QRect
    edit: QRect
    label: QRect
    spinbox: SpinBoxRect
    reset: QRect


class ParamDelegate(QStyledItemDelegate):
    """"""

    open_editor = Signal(QPersistentModelIndex)
    edit_index = Signal(QPersistentModelIndex)
    reset_index = Signal(QPersistentModelIndex)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._edit = CoreIcon(":/odc/iconoir/edit-pencil.svg", )
        self._drag = CoreIcon(":/odc/iconoir/menu.svg")
        self._reset = CoreIcon(":/odc/iconoir/warning-triangle.svg")

        self._mouse = QPoint(0, 0)
        self._edit_down = False
        self._reset_down = False

    def editorEvent(self, event: QEvent, model, option, index) -> bool:

        rects = self._rects(option)

        def _unclick() -> None:
            self._edit_down = False
            self._reset_down = False

        if isinstance(event, QDragEnterEvent):
            print(event)
            _unclick()

        elif isinstance(event, QMouseEvent):
            self._mouse = event.pos()
            inside_edit = rects.edit.contains(event.pos())
            inside_reset = rects.reset.contains(event.pos())
            inside_spinbox = rects.spinbox.bounds.contains(event.pos())

            if inside_edit:
                model.setData(index, "Edit Param", ParamData.TOOLTIP)
            elif inside_reset:
                model.setData(index, "Reset To Default Value", ParamData.TOOLTIP)
            elif rects.drag.contains(event.pos()):
                model.setData(index, "Drag To Reorder", ParamData.TOOLTIP)
            else:
                model.setData(index, "", ParamData.TOOLTIP)

            if event.button() == Qt.MouseButton.LeftButton:
                if event.type() == QMouseEvent.Type.MouseButtonPress:
                    if inside_edit:
                        self._edit_down = True
                        self.edit_index.emit(QPersistentModelIndex(index))
                        QTimer.singleShot(50, _unclick)
                    if inside_reset:
                        self._reset_down = True
                        self.reset_index.emit(QPersistentModelIndex(index))
                        QTimer.singleShot(50, _unclick)
                    if inside_spinbox:
                        self.open_editor.emit(QPersistentModelIndex(index))
                        QTimer.singleShot(50, _unclick)
                elif event.type() == QMouseEvent.Type.MouseButtonRelease:
                    _unclick()

            option.styleObject.viewport().repaint(rects.drag)
            option.styleObject.viewport().repaint(rects.edit)
            option.styleObject.viewport().repaint(rects.reset)

        return super().editorEvent(event, model, option, index)

    def createEditor(
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,  # noqa: ARG002
        index: QModelIndex | QPersistentModelIndex,  # noqa: ARG002
    ) -> QDoubleSpinBox:
        """"""
        editor = QDoubleSpinBox(parent=parent)
        editor.setAlignment(Qt.AlignmentFlag.AlignRight)

        param = self.from_index(index)
        log.debug(f"editing param: {param}")

        if index.isValid():
            editor.setDecimals(index.data(ParamData.DECIMALS))
            editor.setMinimum(index.data(ParamData.MIN))
            editor.setMaximum(index.data(ParamData.MAX))
            editor.setSingleStep(index.data(ParamData.STEP))
            editor.setSuffix(f" {index.data(ParamData.UNIT)}")

        editor.valueChanged.connect(lambda *_, e=editor: self.commitData.emit(e))

        return editor

    def setModelData(
        self,
        editor: QDoubleSpinBox,
        model: ParamModel,
        index: QModelIndex | QPersistentModelIndex
    ) -> None:
        model.setData(index, editor.value(), ParamData.VALUE)

    def setEditorData(self, editor: QDoubleSpinBox, index: QModelIndex | QPersistentModelIndex) -> None:
        new_value = index.data(ParamData.VALUE)
        if index.isValid() and editor.value() != new_value:
            editor.setValue(new_value)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        return QSize(100, 35)

    def updateEditorGeometry(
        self,
        editor: QDoubleSpinBox,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex
    ) -> None:
        rects = self._rects(option)
        editor.setGeometry(rects.spinbox.bounds)

    @staticmethod
    def from_index(index: QModelIndex | QPersistentModelIndex) -> FloatParam:
        return FloatParam(
            value=index.data(ParamData.VALUE),
            default=index.data(ParamData.DEFAULT),
            label=index.data(ParamData.LABEL),
            unit=index.data(ParamData.UNIT),
            step=index.data(ParamData.STEP),
            min_value=index.data(ParamData.MIN),
            max_value=index.data(ParamData.MAX),
            decimals=index.data(ParamData.DECIMALS),
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex
    ) -> None:

        style = QApplication.style()
        palette = cast(QPalette, option.palette)

        with safe_paint(painter) as p:
            param = self.from_index(index)
            p.setClipRect(option.rect)

            rects = self._rects(option)

            p.fillRect(
                option.rect,
                palette.color(QPalette.ColorGroup.Normal, QPalette.ColorRole.Window),
            )

            if param.min_value < param.value < param.max_value:
                rects.spinbox.opts.stepEnabled = QAbstractSpinBox.StepEnabledFlag.StepUpEnabled | QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
            if param.value == param.min_value:
                rects.spinbox.opts.stepEnabled = QAbstractSpinBox.StepEnabledFlag.StepUpEnabled
            if param.value == param.max_value:
                rects.spinbox.opts.stepEnabled = QAbstractSpinBox.StepEnabledFlag.StepDownEnabled

            style.drawComplexControl(QStyle.ComplexControl.CC_SpinBox, rects.spinbox.opts, p)

            style.drawItemText(
                p,
                rects.spinbox.text,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                palette,
                True,
                f"{param.value:.{param.decimals}f} {param.unit}",
                QPalette.ColorRole.Text
            )

            style.drawItemText(
                p,
                rects.label,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                palette,
                True,
                f"{param.label}",
                QPalette.ColorRole.Text
            )

            mode = QIcon.Mode.Active if self._edit_down or self._reset_down else QIcon.Mode.Normal

            p.drawPixmap(
                rects.drag,
                self._drag.pixmap(
                    rects.drag.size(),
                    QIcon.Mode.Disabled,
                    QIcon.State.On,
                ),
            )
            p.drawPixmap(
                rects.edit,
                self._edit.pixmap(
                    rects.edit.size(),
                    mode if (rects.edit.contains(self._mouse) and self._edit_down) else QIcon.Mode.Disabled,
                    QIcon.State.On,
                ),
            )
            p.drawPixmap(
                rects.reset,
                self._reset.pixmap(
                    rects.reset.size(),
                    mode if (rects.reset.contains(self._mouse) and self._reset_down) else QIcon.Mode.Disabled,
                    QIcon.State.On,
                ),
            )

    def _rects(self, option: QStyleOptionViewItem) -> Rects:
        """
        -----------------------------------------
        | 1 | 2 |      3      |      4      | 5 |
        -----------------------------------------
        1. drag
        2. edit
        3. label
        4. spinbox
        5. reset
        """
        style = QApplication.style()
        bounds = cast(QRect, option.rect)
        height = bounds.height()
        spacing = 4

        drag_rect = QRect(bounds.topLeft(), QSize(height, height))
        edit_rect = drag_rect.translated(drag_rect.width() + spacing, 0)

        reset_rect = QRect(bounds.topRight() - QPoint(height, 0), bounds.bottomRight())

        middle_rect = QRect(edit_rect.topRight(), reset_rect.bottomLeft())

        label_rect = middle_rect.adjusted(spacing, 0, (-middle_rect.width() // 2) - spacing, 0)

        spinbox_bounds = middle_rect.adjusted((middle_rect.width() // 2) + spacing, 0, -spacing, 0)

        sb = QStyleOptionSpinBox()
        sb.palette = option.palette
        sb.fontMetrics = option.fontMetrics
        sb.font = option.font
        sb.rect = spinbox_bounds
        sb.frame = True

        spinbox_text = style.subControlRect(
            QStyle.ComplexControl.CC_SpinBox,
            sb,
            QStyle.SubControl.SC_SpinBoxEditField,
        )
        spinbox_text = style.alignedRect(
            Qt.LayoutDirection.LeftToRight,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            spinbox_text.size(),
            spinbox_bounds,
        )

        return Rects(
            drag=drag_rect.marginsRemoved(QMargins(5, 5, 5, 5)),
            edit=edit_rect.marginsRemoved(QMargins(8, 8, 8, 8)),
            label=label_rect,
            spinbox=SpinBoxRect(
                opts=sb,
                bounds=spinbox_bounds,
                text=spinbox_text,
            ),
            reset=reset_rect.marginsRemoved(QMargins(8, 8, 8, 8)),
        )
