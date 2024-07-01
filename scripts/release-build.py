# /// script
# requires-python = ">=3.12"
# dependencies = [
#    "jinja2",
# ]
# ///
import argparse
import platform
import shutil
import subprocess
import sys
import time

from jinja2 import Environment, FileSystemLoader

from lib.utils import cd, DIST_DIR

MACOS_NAME = "ODC Commander.app"
WIN_NAME = "ODC Commander.exe"
LINUX_NAME = "ODC Commander.bin"


class ReleaseError(Exception):
    """error in the release process"""


def release(exe_name: str, *, keep_deployment_files: bool = False) -> None:
    print("PySide6 Deploy...")

    shutil.rmtree(DIST_DIR, ignore_errors=True)
    print("/dist dir removed...")

    time.sleep(1)

    with cd("src") as wd:
        env = Environment(loader=FileSystemLoader(wd), autoescape=True)
        pysidedeploy_template = env.get_template("pysidedeploy.spec.jinja2")

        spec_txt = pysidedeploy_template.render(
            {
                "icon": str(wd / "resources" / "odc" / "app" / "icon.png"),
                "python_path": sys.executable,
            }
        )
        (wd / "pysidedeploy.spec").write_text(spec_txt)

        expected_app_build = wd / exe_name
        dist_app_target = DIST_DIR / exe_name

        extra_args = [
            "--force"
        ]
        if keep_deployment_files:
            extra_args.append("--keep-deployment-files")

        subprocess.check_call(
            [
                "pyside6-deploy",
                *extra_args,
                f'--c={wd / "pysidedeploy.spec"}',
            ],
            text=True,
        )

        if expected_app_build.exists():
            DIST_DIR.mkdir(parents=True, exist_ok=True)
            # move from build dir to `dist` dir
            shutil.move(expected_app_build, dist_app_target)
            print(f"Moved app build to {dist_app_target}")
        else:
            raise ReleaseError(f"App build not found after deploy process completed. {expected_app_build}")


def bundle_macos_dmg(exe_name: str, *, keep_build_files: bool = False) -> None:
    dmg_name = exe_name.replace(".app", ".dmg")

    dmg_target = DIST_DIR / dmg_name
    dmg_target.unlink(missing_ok=True)

    with cd("dist"):
        subprocess.check_call(
            ["hdiutil", "create", "-volname", exe_name, "-srcfolder", exe_name, "-ov", "-format", "UDZO", dmg_name],
            text=True,
        )

    if not keep_build_files:
        shutil.rmtree(DIST_DIR / exe_name)


def linux_remove_bin_extension(exe_name: str) -> None:
    with_bin = DIST_DIR / exe_name
    without_bin = DIST_DIR / exe_name.removesuffix(".bin")

    with_bin.rename(without_bin)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--keep-build-files", action="store_false")

    args = parser.parse_args()

    plat = platform.system()
    if plat == "Darwin":
        release(MACOS_NAME, keep_deployment_files=args.keep_build_files)
        bundle_macos_dmg(MACOS_NAME, keep_build_files=args.keep_build_files)
    elif plat == "Windows":
        release(WIN_NAME)
    elif plat == "Linux":
        release(LINUX_NAME)
        linux_remove_bin_extension(LINUX_NAME)
    else:
        raise Exception(f"Unsupported platform {plat}")  # noqa: TRY002
