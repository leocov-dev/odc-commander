import shutil
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class BuildHookCustom(BuildHookInterface):
    """
    Download vendored copies of arduino-cli for possible inclusion in the build
    """

    # https://github.com/arduino/arduino-cli/releases/tag/v1.0.4
    url_map = {
        "Linux":        "https://github.com/arduino/arduino-cli/releases/download/v1.0.4/arduino-cli_1.0.4_Linux_64bit.tar.gz",
        "Darwin-arm":   "https://github.com/arduino/arduino-cli/releases/download/v1.0.4/arduino-cli_1.0.4_macOS_ARM64.tar.gz",
        "Darwin-intel": "https://github.com/arduino/arduino-cli/releases/download/v1.0.4/arduino-cli_1.0.4_macOS_64bit.tar.gz",
        "Windows":      "https://github.com/arduino/arduino-cli/releases/download/v1.0.4/arduino-cli_1.0.4_Windows_64bit.zip",
    }

    @property
    def vendor(self) -> Path:
        v = self.repo / "src" / "vendor"
        v.mkdir(exist_ok=True, parents=True)
        return v

    @property
    def repo(self) -> Path:
        return Path(self.root)

    def initialize(self, _: str, __: dict[str, Any]) -> None:
        if not self.config.get("arduino-cli", False):
            return

        for plat, url in self.url_map.items():
            plat_dir = self.vendor / plat
            if plat_dir.exists():
                continue

            self._dl_file(url, plat)

    def clean(self, _: list[str]):
        for item in self.vendor.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    def _dl_file(self, dl_url: str, dir_name: str):
        self.app.display_info(f"Downloading: {dir_name} - {dl_url}")

        fn = dl_url.split("/")[-1]
        target = self.vendor / fn
        urlretrieve(dl_url, target)

        if not target.exists():
            raise Exception(f"downloaded file {target.relative_to(self.repo)} does not exist...")

        shutil.unpack_archive(target, self.vendor / dir_name)

        target.unlink()
