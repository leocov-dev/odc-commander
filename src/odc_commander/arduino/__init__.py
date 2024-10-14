from typing import Literal

from odc_commander import DATA_DIR, ROOT_DIR

FIRMWARE_ROOT = DATA_DIR / "firmware"

BinType = Literal["bin", "elf", "hex"]

VENDOR_ROOT = ROOT_DIR / "vendor"
