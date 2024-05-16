import os
import sys

from PySide6.QtWidgets import QApplication
from serial import serial_for_url
import pty

if __name__ == '__main__':

    pty.openpty()

    master, slave = pty.openpty()
    s_name = os.ttyname(slave)
    print(s_name)

    qtapp = QApplication()

    sys.exit(qtapp.exec())