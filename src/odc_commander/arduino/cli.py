import json
import subprocess
from json import JSONDecodeError
from pathlib import Path
from typing import Any, cast

from odc_commander.arduino.errors import ODCArduinoCliError

__cli_exe: Path | None = None


def set_cli_exe(exe: Path) -> None:
    global __cli_exe

    if not exe or not exe.is_file() or not exe.exists():
        raise ODCArduinoCliError(f"Invalid Arduino CLI path: {exe}")

    __cli_exe = exe

    try:
        arduino_cli("version")
    except:
        __cli_exe = None
        raise ODCArduinoCliError(f"Invalid Arduino CLI check: {exe}")


def _cli_exe() -> Path:
    if __cli_exe is None:
        raise ODCArduinoCliError("arduino-cli path is not set")
    return __cli_exe


def arduino_cli(cmd: str, *args: str) -> dict[str, Any]:
    try:
        result = subprocess.check_output(
            [  # noqa: S607
                _cli_exe(),
                cmd,
                "--format",
                "json",
                *args,
            ],
            text=True,
        )
    except FileNotFoundError as e:
        raise ODCArduinoCliError("Can't find arduino-cli, please install it first.") from e
    except subprocess.CalledProcessError as e:
        result = e.output

    try:
        return cast(dict[str, Any], json.loads(result or "{}"))
    except JSONDecodeError:
        return {}
