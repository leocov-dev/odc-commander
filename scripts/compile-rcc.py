# /// script
# requires-python = ">=3.12"
# ///
import subprocess

from lib.utils import REPO_ROOT


def compile_rcc() -> None:
    print("Compiling RCC...")
    subprocess.check_call(
        [
            "pyside-app-core-compile-rcc",
            "src/odc_commander",
            "--extra-resource-root",
            str(REPO_ROOT / "src" / "resources" / "odc"),
            "--debug",
        ],
    )


if __name__ == "__main__":
    compile_rcc()
