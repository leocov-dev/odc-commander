from importlib import metadata

from loguru import logger
from pyside_app_core.errors import excepthook
from pyside_app_core.log import configure_get_logger_func
from pyside_app_core.qt import application_service
from pyside_app_core.style.theme import QssTheme

from odc_commander.app import OdcCommanderApp

configure_get_logger_func(lambda: logger)


class CustomTheme(QssTheme):
    ...


version = metadata.version("odc_commander")

excepthook.install_excepthook()
application_service.set_app_version(version)
application_service.set_app_id("com.odc.commander")
application_service.set_app_name("Open Dynamic Clamp Commander")
application_service.set_app_theme(CustomTheme())

app = OdcCommanderApp()

app.launch()
