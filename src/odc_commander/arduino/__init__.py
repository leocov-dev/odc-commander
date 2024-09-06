from pathlib import Path
from typing import Literal

FIRMWARE_ROOT = Path(__file__).parent.parent.parent / "odc_firmware"

BinType = Literal["bin", "elf", "hex"]
