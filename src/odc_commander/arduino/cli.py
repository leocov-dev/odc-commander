import json
import platform
import subprocess
from json import JSONDecodeError
from pathlib import Path
from typing import Any, cast

from odc_commander import VENDOR_DIR
from odc_commander.arduino.errors import ODCArduinoCliError
from pyside_app_core import log


def _default_cli() -> Path | None:
    match platform.system():
        case "Windows":
            return VENDOR_DIR / "arduino-cli.exe"
        case _:
            return VENDOR_DIR / "arduino-cli"


__cli_exe: Path | None = _default_cli()


def set_cli_exe(exe: Path) -> None:
    global __cli_exe

    if not exe or not exe.is_file() or not exe.exists():
        raise ODCArduinoCliError(f"Invalid Arduino CLI path: {exe}")

    __cli_exe = exe

    try:
        arduino_cli("version")
    except Exception as e:
        __cli_exe = None
        raise ODCArduinoCliError(f"Invalid Arduino CLI check: {exe}") from e


def _cli_exe() -> Path:
    log.debug(f"arduino-cli: {__cli_exe}")
    if not __cli_exe or (not __cli_exe.is_file() and not __cli_exe.exists()):
        raise ODCArduinoCliError("arduino-cli path is not set")
    return __cli_exe


def arduino_cli(cmd: str, *args: str) -> dict[str, Any]:
    try:
        result = subprocess.check_output(
            [
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
