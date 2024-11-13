import time
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pyside_app_core import log
from pyside_app_core.mixin.settings_mixin import SettingsMixin

from odc_commander.interfaces.project.v1 import ProjectComponentData
from odc_commander.interfaces.project_component import ProjectComponentInterface


class ProjectLoadingError(Exception):
    def __init__(self, file_path: Path):
        super().__init__(f"Could not load project from {file_path}")


class Project(BaseModel):
    schema_version: Literal["v1"] = "v1"

    components: list[ProjectComponentData] = Field(default_factory=list)


class ProjectService(SettingsMixin, QObject):
    unsaved_changes = Signal(str)
    project_loaded = Signal(str)
    project_saved = Signal(str)
    progress = Signal(int, int)

    @property
    def name(self) -> str:
        return self.file_path.name if self.file_path else "Unsaved"

    @property
    def file_path(self) -> Path | None:
        return self._file_path

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)
        self._components: dict[str, ProjectComponentInterface[Any]] = {}

        self._file_path: Path | None = None

        # ---
        QApplication.instance().aboutToQuit.connect(self._store_current_project)  # type: ignore[union-attr]

    def register_component[T](self, component: ProjectComponentInterface[T]) -> None:
        self._components[component.component_type] = component
        component.unsaved_changes.connect(  # type: ignore[call-overload]
            lambda: log.debug(f"unsaved changes: {component}")
        )
        component.unsaved_changes.connect(lambda: self.unsaved_changes.emit(self.name))  # type: ignore[call-overload]

    def new(self) -> None:
        self._file_path = None
        self.unsaved_changes.emit(self.name)
        for comp in self._components.values():
            comp.restore_defaults()

    def save_as(self, file_path: Path) -> None:
        self._file_path = file_path
        self.save()

    def save(self) -> None:
        if not self.file_path:
            log.warning("can't save project, file path not set")
            return

        proj = Project(
            components=[c.serialize() for c in self._components.values()],
        )

        for i in range(20):
            time.sleep(0.1)
            self.progress.emit(i + 1, 20)
            QApplication.processEvents()

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(proj.model_dump_json(indent=4))
        self.project_saved.emit(self.name)

    def load(self, proj_file: Path) -> None:
        if not proj_file.exists():
            raise ProjectLoadingError(proj_file)

        # TODO: rollback to prev state on errors???

        proj = Project.model_validate_json(proj_file.read_text())
        for p in proj.components:
            comp = self._components.get(p.component_type)
            if comp is None:
                log.warning(f"failed to load component {p.component_type}")
                continue
            comp.deserialize(p)

        self._file_path = proj_file
        self.project_loaded.emit(self.name)

    def _store_current_project(self) -> None:
        self.store_setting("last-open-project", self._file_path)
