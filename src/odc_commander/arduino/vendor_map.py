from typing import NamedTuple, TypedDict

from odc_commander.arduino.commands import install_core


class Vendor(NamedTuple):
    url: str
    core: str
    boards: dict[str, str]

    def install_core(self) -> None:
        install_core(self.core, [self.url])


# dependency for other samd cores
ARDUINO_SAMD = Vendor(
    url="",
    core="arduino:samd",
    boards={},
)
ADAFRUIT_SAMD = Vendor(
    url="https://adafruit.github.io/arduino-board-index/package_adafruit_index.json",
    core="adafruit:samd",
    boards={
        "itsybitsym4": "adafruit:samd:adafruit_itsybitsy_m4",
        "grandcentralm4": "adafruit:samd:adafruit_grandcentral_m4",
    },
)
SPARKFUN_SAMD = Vendor(
    url="https://raw.githubusercontent.com/sparkfun/Arduino_Boards/main/IDE_Board_Manager/package_sparkfun_index.json",
    core="SparkFun:samd",
    boards={
        "samd51thingplus": "SparkFun:samd:samd51_thing_plus",
        "samd51micromod": "SparkFun:samd:micromod_samd51",
    },
)
TEENSY = Vendor(
    url="https://www.pjrc.com/teensy/package_teensy_index.json",
    core="teensy:avr",
    boards={"teensy36": "teensy:avr:teensy35", "teensy35": "teensy:avr:teensy35", "teensy31": "teensy:avr:teensy31"},
)


class ProductData(TypedDict, total=True):
    name: str
    display_name: str
    board: str


ProductMap = dict[int, ProductData]


class VendorData(TypedDict, total=True):
    name: str
    products: ProductMap


VendorMap = dict[int, VendorData]

VENDOR_MAP: VendorMap = {
    9114: {
        "name": "Adafruit",
        "products": {
            32811: {
                "name": "ItsyBitsyM4",
                "display_name": "OpenDynamicClamp 1.x",
                "board": ADAFRUIT_SAMD.boards["itsybitsym4"],
            },
            43: {
                "name": "ItsyBitsyM4-Bootloader",
                "display_name": "OpenDynamicClamp 1.x",
                "board": ADAFRUIT_SAMD.boards["itsybitsym4"],
            },
            # grand central???
        },
    },
    6991: {
        "name": "SparkFun Electronics",
        "products": {
            61462: {
                "name": "SAMD51 Thing Plus",
                "display_name": "OpenDynamicClamp 1.x",
                "board": SPARKFUN_SAMD.boards["samd51thingplus"],
            },
            -1: {
                "name": "SparkFun MicroMod SAMD51 Processor Board",
                "display_name": "OpenDynamicClamp 1.x",
                "board": SPARKFUN_SAMD.boards["samd51micromod"],
            },
        },
    },
    5824: {
        "name": "Teensyduino",
        "products": {
            1155: {
                "name": "Teensy 3.6",
                "display_name": "OpenDynamicClamp 1.x",
                "board": TEENSY.boards["teensy36"],
            },
            -1: {
                "name": "Teensy 3.5",
                "display_name": "OpenDynamicClamp 1.x",
                "board": TEENSY.boards["teensy35"],
            },
            -2: {
                "name": "Teensy 3.1 / 3.2",
                "display_name": "OpenDynamicClamp 1.x",
                "board": TEENSY.boards["teensy31"],
            },
        },
    },
}
