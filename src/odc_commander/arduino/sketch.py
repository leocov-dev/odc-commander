from pathlib import Path

from odc_commander.arduino import BinType, FIRMWARE_ROOT


def get_sketch(name: str) -> Path:
    name = name.removesuffix(".ino")

    expected = FIRMWARE_ROOT / name / f"{name}.ino"
    if not expected.exists() or not expected.is_file():
        raise FileNotFoundError(f"Sketch {name} not found at: {expected}")

    return expected


def get_sketch_bin(name: str, bin_type: BinType = "hex") -> Path:
    expected = get_sketch(name).with_suffix(f".ino.{bin_type}")
    if not expected.exists() or not expected.is_file():
        raise FileNotFoundError(f"Sketch BIN {name}.{bin_type} not found at: {expected}")

    return expected
