import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any
from collections.abc import Mapping
from urllib.request import urlretrieve

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class BuildHookCustom(BuildHookInterface):
    """
    Download vendored copies of arduino-cli for possible inclusion in the build
    """

    # https://github.com/arduino/arduino-cli/releases/tag/v1.0.4
    _URL_MAP: Mapping[str, list[str]] = {
        "linux": [
            "https://github.com/arduino/arduino-cli/releases/download/v1.0.4/arduino-cli_1.0.4_Linux_64bit.tar.gz",
        ],
        "darwin": [
            "https://github.com/arduino/arduino-cli/releases/download/v1.0.4/arduino-cli_1.0.4_macOS_ARM64.tar.gz",
            "https://github.com/arduino/arduino-cli/releases/download/v1.0.4/arduino-cli_1.0.4_macOS_64bit.tar.gz",
        ],
        "windows": [
            "https://github.com/arduino/arduino-cli/releases/download/v1.0.4/arduino-cli_1.0.4_Windows_64bit.zip",
        ],
    }
    _MAC = 2

    @property
    def vendor(self) -> Path:
        v = self.repo / "src" / "vendor"
        v.mkdir(exist_ok=True, parents=True)
        return v

    @property
    def repo(self) -> Path:
        return Path(self.root)

    def clean(self, _: list[str]):
        for item in self.vendor.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    def initialize(self, _: str, build_data: dict[str, Any]) -> None:
        build_data["artifacts"].extend(self._fetch_arduino_cli())

    def _fetch_arduino_cli(self) -> list[str]:
        if not self.config.get("arduino-cli", False):
            self.app.display_warning("arduino-cli download is disabled")
            return []

        plat = platform.system().lower()

        if plat not in self._URL_MAP:
            raise ValueError(f"Platform: {plat} not supported")

        if existing := next(self.vendor.glob("arduino-cli*"), None):
            self.app.display_warning(f"arduino-cli already cached: {existing}")
            return []

        for url in self._URL_MAP[plat]:
            self._dl_file(url, plat)

        if plat == "darwin":
            to_merge: list[Path] = list(self.vendor.glob("arduino-cli*macOS*"))
            if len(to_merge) != self._MAC:
                raise ValueError("problems merging macOS arches")

            # merge 2 arches into universal
            subprocess.check_call(
                [
                    "lipo",
                    "-create",
                    "-output",
                    str(self.vendor / "arduino-cli"),
                    *[str(m) for m in to_merge],
                ],
            )

            # assert cli is working, probably...
            subprocess.run(
                ["arduino-cli", "version"],
                cwd=str(self.vendor),
                capture_output=True,
                check=True,
            )

            for i in to_merge:
                i.unlink()

        elif plat == "linux":
            cli: Path | None = next(self.vendor.glob("arduino-cli*"), None)
            if not cli and not cli.exists():
                raise ValueError("cannot find linux arduino-cli executable")

            cli.rename(self.vendor / "arduino-cli")
        elif plat == "windows":
            cli: Path | None = next(self.vendor.glob("arduino-cli*.exe"), None)
            if not cli and not cli.exists():
                raise ValueError("cannot find windows arduino-cli executable")

            cli.rename(self.vendor / "arduino-cli.exe")

        return [str(p) for p in self.vendor.glob("arduino-cli*")]

    def _dl_file(self, dl_url: str, dir_name: str):
        self.app.display_info(f"Downloading: {dir_name} - {dl_url}")

        fn = dl_url.split("/")[-1]
        target = self.vendor / fn
        urlretrieve(dl_url, target)

        if not target.exists():
            raise Exception(f"downloaded file {target.relative_to(self.repo)} does not exist...")

        shutil.unpack_archive(target, self.vendor / dir_name)
        cli = next((self.vendor / dir_name).glob("arduino-cli*"))
        cli.rename(self.vendor / f"{fn.removesuffix('.tar.gz').removesuffix('.zip')}{cli.suffix}")

        target.unlink()
        shutil.rmtree(self.vendor / dir_name)
