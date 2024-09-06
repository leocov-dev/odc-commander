import tempfile
from collections.abc import Callable
from pathlib import Path

from PySide6.QtSerialPort import QSerialPortInfo
from pyside_app_core import log

from odc_commander.arduino import BinType
from odc_commander.arduino.cli import arduino_cli
from odc_commander.arduino.errors import ODCArduinoCliError, ODCArduinoCompileError
from odc_commander.arduino.schemas import Cores


def list_cores() -> Cores:
    return Cores.model_validate(arduino_cli("core", "list"))


def install_core(core: str, additional_urls: list[str] | None = None) -> None:
    cores = [c.id for c in list_cores().platforms]
    if core in cores:
        log.debug(f"core {core} already installed")
        return

    additional_urls_flag = []
    if additional_urls:
        additional_urls_flag.append("--additional-urls")
        additional_urls_flag.append(",".join([u.strip() for u in additional_urls]))

    arduino_cli("core", *additional_urls_flag, "install", core)


def compile_sketch(
    sketch: Path,
    board: str,
    bin_callback: Callable[[Path], None] | None = None,
    bin_type: BinType = "hex",
    target_port: QSerialPortInfo | str | None = None,
) -> None:
    with tempfile.TemporaryDirectory(prefix="odc-firmware-compile") as temp_dir:
        expected_bin = Path(temp_dir) / f"{sketch.name}.{bin_type}"

        args = [
            "--fqbn",
            board,
            "--output-dir",
            temp_dir,
        ]

        if target_port:
            if isinstance(target_port, QSerialPortInfo):
                target_port = target_port.systemLocation()
            args.extend(["--upload", "--port", target_port, "--verify"])

        log.debug(f"compile args: {args}")

        result = arduino_cli("compile", *args, str(sketch.expanduser().absolute()))

        if callable(bin_callback):
            bin_callback(expected_bin)

    if not result.get("success", False):
        raise ODCArduinoCompileError(sketch, result)


def upload_bin(
    bin_path: Path,
    board: str,
    target_port: QSerialPortInfo | str,
) -> None:
    if isinstance(target_port, QSerialPortInfo):
        target_port = target_port.systemLocation()

    result = arduino_cli(
        "upload",
        str(bin_path),
        "--fqbn",
        board,
        "--port",
        target_port,
        "--verify",
    )

    if not result.get("success", False):
        line = "-" * 80
        msg = f"compile failed for: {bin_path.name}."

        if uploader_error := result.get("uploader_error"):
            msg = f"{msg}\n{line}\n{uploader_error}"

        raise ODCArduinoCliError(msg)
