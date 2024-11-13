from typing import Protocol

from odc_commander.interfaces.project.v1 import _ComponentBase
from PySide6.QtCore import Signal
from typing_extensions import TypeVar

T = TypeVar("T", bound=_ComponentBase)


class ProjectComponentInterface[T](Protocol):
    unsaved_changes: Signal

    @property
    def component_type(self) -> str: ...

    def serialize(self) -> T: ...

    def deserialize(self, data: T) -> None: ...

    def restore_defaults(self) -> None: ...
