import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Literal

ADAFRUIT_URL = "https://adafruit.github.io/arduino-board-index/package_adafruit_index.json"
ADAFRUIT_SAMD = "adafruit:samd"


def install_core(core: str, additional_urls: list[str]) -> None:
    additional_urls_flag = []
    if additional_urls:
        additional_urls_flag.append("--additional-urls")
        additional_urls_flag.append(",".join(additional_urls))

    subprocess.check_call(
        [
            "arduino-cli",
            "core",
            *additional_urls_flag,
            "install",
            core
        ]
    )


BinType = Literal["bin", "elf", "hex"]


def compile_sketch(sketch: Path, board: str, bin_callback: Callable[[Path], None], bin_type: BinType = "hex") -> None:
    with tempfile.TemporaryDirectory(prefix="odc-firmware-compile") as temp_dir:
        expected_bin = Path(temp_dir) / f"{sketch.name}.{bin_type}"

        subprocess.check_call(
            [
                "arduino-cli",
                "compile",
                "--fqbn", board,
                "--output-dir", temp_dir,
                str(sketch.expanduser().absolute())
            ]
        )

        bin_callback(expected_bin)
