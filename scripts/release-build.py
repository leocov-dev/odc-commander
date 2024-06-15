# /// script
# requires-python = ">=3.12"
# dependencies = [
#    "jinja2",
# ]
# ///
import platform
import shutil
import subprocess
import sys
import time

from jinja2 import Environment, FileSystemLoader

from lib.utils import cd, DIST_DIR, REPO_ROOT

MACOS_NAME = "ODC Commander.app"
WIN_NAME = "ODC Commander.exe"
LINUX_NAME = "ODC Commander.bin"


def release(exe_name: str) -> None:
    print("PySide6 Deploy...")

    shutil.rmtree(DIST_DIR, ignore_errors=True)
    print("/dist dir removed...")

    time.sleep(1)

    with cd("src") as wd:
        env = Environment(loader=FileSystemLoader(wd), autoescape=True)
        pysidedeploy_template = env.get_template("pysidedeploy.spec.jinja2")

        spec_txt = pysidedeploy_template.render(
            {
                "icon":        str(wd / "resources" / "odc" / "app" / "icon.png"),
                "python_path": sys.executable,
            }
        )
        (wd / "pysidedeploy.spec").write_text(spec_txt)

        expected_app_build = wd / exe_name
        dist_app_target = DIST_DIR / exe_name

        subprocess.check_call(
            [
                "pyside6-deploy",
                "--force",
                f'--c={wd / "pysidedeploy.spec"}',
            ],
        )

        if expected_app_build.exists():
            DIST_DIR.mkdir(parents=True, exist_ok=True)
            # move from build dir to `dist` dir
            shutil.move(expected_app_build, dist_app_target)
            print(f"Moved app build to {dist_app_target}")
        else:
            raise Exception(f"App build not found after deploy process completed. {expected_app_build}")


def bundle_macos_dmg(exe_name: str) -> None:
    dmg_name = exe_name.replace(".app", ".dmg")

    dmg_target = DIST_DIR / dmg_name
    dmg_target.unlink(missing_ok=True)

    with cd("dist"):
        subprocess.check_call(
            ["hdiutil", "create", "-volname", exe_name, "-srcfolder", exe_name, "-ov", "-format", "UDZO", dmg_name],
        )

    shutil.rmtree(DIST_DIR / exe_name)

if __name__ == "__main__":
    plat = platform.system()
    if plat == "Darwin":
        release(MACOS_NAME)
        bundle_macos_dmg(MACOS_NAME)
    elif plat == "Windows":
        release(WIN_NAME)
    elif plat == "Linux":
        release(LINUX_NAME)
    else:
        raise Exception(f"Unsupported platform {plat}")  # noqa: TRY002
