from pathlib import Path
from typing import NamedTuple, TypedDict

from PySide6.QtCore import QTimer, Signal
from PySide6.QtSerialPort import QSerialPortInfo
from PySide6.QtWidgets import QFileDialog, QPushButton, QVBoxLayout, QWidget
from pyside_app_core import log
from pyside_app_core.types.file_picker import FileConfig
from pyside_app_core.ui.widgets.file_picker import FilePicker
from pyside_app_core.utils.time_ms import SECONDS

from odc_commander.arduino.commands import compile_sketch, upload_bin


class UploaderError(Exception):
    """"""


class UploadTarget(NamedTuple):
    port: QSerialPortInfo
    board: str


class SketchData(TypedDict):
    sketch: Path | None
    uploader_btn_text: str
    readonly: bool


SketchMap = dict[int, SketchData]


class ArduinoUploader(QWidget):
    about_to_upload = Signal()
    upload_complete = Signal()

    def __init__(
        self,
        *,
        sketch: Path | None = None,
        upload_btn_text: str = "Upload Sketch",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        _ly = QVBoxLayout()
        _ly.setContentsMargins(0, 0, 0, 0)

        self._target: UploadTarget | None = None

        # ----
        self.setLayout(_ly)

        # ---
        self._file_picker = FilePicker(
            heading="Firmware",
            config=FileConfig(
                caption="Select Arduino sketch file or binary",
                selection_filter="Arduino sketch file (*.ino *.bin *.hex *.elf)",
                starting_directory=None,
                options=QFileDialog.Option.ReadOnly,
            ),
            truncate_path=1,
            parent=self,
        )
        _ly.addWidget(self._file_picker)

        self._upload_btn = QPushButton(upload_btn_text)
        _ly.addWidget(self._upload_btn)

        # -----
        if sketch:
            self._file_picker.set_file_path(sketch)

        # -----
        self._upload_btn.clicked.connect(self._trigger_upload)
        self._file_picker.path_updated.connect(self._on_path_changed)

    def set_active_port(self, port: QSerialPortInfo | None, board: str) -> None:
        if not port or not board:
            self._target = None
        else:
            self._target = UploadTarget(
                port=port,
                board=board,
            )

    def set_current_data(
        self,
        file_path: Path | None,
        btn_text: str,
        readonly: bool,
    ) -> None:
        log.debug(f"set current tab data: {file_path}, {btn_text}, {readonly}")

        self._upload_btn.setText(btn_text or "Upload Sketch")

        if not file_path:
            self._file_picker.clear()
        else:
            self._file_picker.set_file_path(file_path)

        self._file_picker.setReadOnly(readonly)
        self._file_picker.setDisabled(readonly)

    def setReadOnly(self, val: bool) -> None:
        self._file_picker.setReadOnly(val)

    def _on_path_changed(self, path: Path | None) -> None:
        log.debug(f"on_path_changed: {path}, {path.is_file() if path is not None else None}")
        self._upload_btn.setEnabled(bool(path and path.is_file()))

    def _trigger_upload(self) -> None:
        if not self._target:
            raise UploaderError("No port selected")
        if not self._file_picker.file_path:
            raise UploaderError("No file selected")

        self.about_to_upload.emit()

        QTimer.singleShot(1 * SECONDS, self._do_upload)

    def _assert_picker_data(self) -> None:
        if not self._file_picker or not self._target or not self._file_picker.file_path:
            raise UploaderError("file and target unset for unknown reasons")

    def _do_upload(self) -> None:
        try:
            self._assert_picker_data()

            if self._file_picker and self._target and self._file_picker.file_path:
                log.info(f"Uploading: {self._file_picker.file_path.name} to {self._target.port.systemLocation()}")

                path = self._file_picker.file_path
                if path.suffix == ".ino":
                    compile_sketch(
                        sketch=path,
                        board=self._target.board,
                        target_port=self._target.port,
                    )
                elif path.suffix in [".bin", ".hex", ".elf"]:
                    upload_bin(
                        bin_path=path,
                        board=self._target.board,
                        target_port=self._target.port,
                    )
        finally:
            QTimer.singleShot(2 * SECONDS, self.upload_complete.emit)
