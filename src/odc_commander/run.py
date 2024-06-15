from loguru import logger
from pyside_app_core.errors import excepthook
from pyside_app_core.log import configure_get_logger_func
from pyside_app_core.qt.application_service import AppMetadata
from pyside_app_core.qt.standard.error_dialog import ErrorDialog

from odc_commander import __version__
from odc_commander.app import OdcCommanderApp

configure_get_logger_func(lambda: logger)

excepthook.install_excepthook(ErrorDialog)
AppMetadata.init(
    "com.odc.commander",
    "ODC Commander",
    __version__,
    ":/odc/app/icon.png",
    None,
    "https://github.com/leocov-dev/odc-commander",
    "https://github.com/leocov-dev/odc-commander/issues",
)

app = OdcCommanderApp()


def run() -> None:
    app.launch()
