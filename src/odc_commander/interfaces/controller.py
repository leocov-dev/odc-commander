from typing import Generic, TypeVar

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget

CC = TypeVar("CC", bound=QObject)


class ControllerView(QWidget, Generic[CC]):
    TAB_NAME: str = ""

    def __init__(
        self,
        controller: CC,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)

        self._controller: CC = controller

    @property
    def controller(self) -> CC:
        return self._controller
