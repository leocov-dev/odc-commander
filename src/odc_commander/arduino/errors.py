from pathlib import Path
from typing import Any


class ODCArduinoCliError(Exception):
    """Raised when an arduino-cli command fails."""

    def __init__(self, msg: str, data: dict[str, Any] | None = None) -> None:
        super().__init__(msg)

        self._data = data or {}


class ODCArduinoCompileError(ODCArduinoCliError):
    def __init__(self, sketch: Path, data: dict[str, Any]) -> None:
        super().__init__(f"Compile failed for: {sketch.name}", data)
