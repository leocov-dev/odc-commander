from PySide6 import QtWidgets
from pyside_app_core.frameless.base_window import FramelessBaseMixin

from core_plus.widgets.connection_manager import ConnectionManager


class OdcMainWindow(FramelessBaseMixin, QtWidgets.QMainWindow):
    """"""

    def __init__(self):
        super(OdcMainWindow, self).__init__(parent=None)

        self.statusBar().showMessage("Disconnected")

        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)

        _ly = QtWidgets.QVBoxLayout()
        _ly.setSpacing(0)
        _ly.setContentsMargins(0, 0, 0, 0)
        central.setLayout(_ly)

        self.main_container = QtWidgets.QWidget(self)
        self.main_container.setLayout(QtWidgets.QVBoxLayout())
        _ly.addWidget(self.main_container)

        self._connection_manager = ConnectionManager(self)
        _ly.addWidget(self._connection_manager)

    def add_controller_view(self, view):
        view.setParent(self)
        self.main_container.layout().addWidget(view)
        # self.main_container.addTab(view, view.__class__.__name__)
