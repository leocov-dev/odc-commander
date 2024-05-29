import os
import pty
import sys

from loguru import logger
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    pty.openpty()

    master, slave = pty.openpty()
    s_name = os.ttyname(slave)
    logger.debug(s_name)

    qtapp = QApplication()

    sys.exit(qtapp.exec())
