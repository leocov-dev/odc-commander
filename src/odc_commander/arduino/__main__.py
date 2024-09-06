import shutil
from pathlib import Path

import odc_commander.arduino.sketch
from odc_commander import arduino
from odc_commander.arduino import commands
from odc_commander.arduino.vendor_map import ARDUINO_SAMD, ADAFRUIT_SAMD, SPARKFUN_SAMD, TEENSY


def save_bin(bin_path: Path) -> None:
    shutil.copy(bin_path, arduino.FIRMWARE_ROOT / bin_path.name.removesuffix(bin_path.suffix).removesuffix(".ino"))


def main() -> None:
    ARDUINO_SAMD.install_core()
    ADAFRUIT_SAMD.install_core()
    SPARKFUN_SAMD.install_core()
    TEENSY.install_core()

    for item in arduino.FIRMWARE_ROOT.glob("*"):
        if not item.is_dir():
            continue
        sketch = item.name
        print("-" * 80)
        print("processing:", sketch)

        commands.compile_sketch(
            odc_commander.arduino.sketch.get_sketch("calibration-input-output"),
            ADAFRUIT_SAMD.boards["itsybitsym4"],
            save_bin,
        )

        output = odc_commander.arduino.sketch.get_sketch_bin("calibration-input-output")
        print("   created:", output.relative_to(arduino.FIRMWARE_ROOT.parent))


# ------------------------------------------------------------------------------
main()
