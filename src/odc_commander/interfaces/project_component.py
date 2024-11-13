from typing import Protocol

from pydantic import BaseModel
from PySide6.QtCore import Signal


class ProjectComponentInterface[T: BaseModel](Protocol):
    unsaved_changes: Signal

    @property
    def component_type(self) -> str: ...

    def serialize(self) -> T: ...

    def deserialize(self, data: T) -> None: ...

    def restore_defaults(self) -> None: ...
