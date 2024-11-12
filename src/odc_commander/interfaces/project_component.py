from typing import Protocol

from PySide6.QtCore import Signal

from odc_commander.interfaces.project.v1 import ProjectComponentData


class ProjectComponentInterface(Protocol):
    unsaved_changes: Signal

    @property
    def component_type(self) -> str: ...

    def serialize(self) -> ProjectComponentData: ...

    def deserialize(self, data: ProjectComponentData) -> None: ...

    def restore_defaults(self) -> None: ...
