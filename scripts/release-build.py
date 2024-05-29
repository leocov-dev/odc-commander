# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "jinja2",
# ]
# ///
import platform
import shutil
import subprocess
import sys

from jinja2 import Environment, FileSystemLoader

from lib.utils import cd, REPO_ROOT

macos_name = "OpenDynamicClamp Commander.app"
win_name = "OpenDynamicClamp Commander.exe"
linux_name = "OpenDynamicClamp Commander"


def release(exe_name: str) -> None:
    print("PySide6 Deploy...")
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

        app_build = wd / exe_name

        # delete old app executable
        app_target = REPO_ROOT / "dist" / exe_name
        shutil.rmtree(app_target, ignore_errors=True)

        subprocess.check_call(
            [
                "pyside6-deploy",
                f'--c={wd / "pysidedeploy.spec"}',
            ],
        )

        if app_build.exists():
            # move from build dir to `dist` dir
            shutil.move(app_build, app_target.parent)


def bundle_macos_dmg(exe_name: str) -> None:
    dmg_name = exe_name.replace(".app", ".dmg")

    dmg_target = REPO_ROOT / "dist" / dmg_name
    dmg_target.unlink(missing_ok=True)

    with cd("dist"):
        subprocess.check_call(
            ["hdiutil", "create", "-volname", exe_name, "-srcfolder", exe_name, "-ov", "-format", "UDZO", dmg_name],
        )


if __name__ == "__main__":
    plat = platform.system()
    if plat == "Darwin":
        release(macos_name)
        bundle_macos_dmg(macos_name)
    elif plat == "Windows":
        release(win_name)
    elif plat == "Linux":
        release(linux_name)
    else:
        raise Exception(f"Unsupported platform {plat}")  # noqa: TRY002
