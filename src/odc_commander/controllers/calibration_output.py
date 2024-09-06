from PySide6.QtCore import QObject, Qt, QTimerEvent
from pyside_app_core.services.serial_service.types import Encodable

from odc_commander.interfaces.controller import Controller, SerialConfig


class CalibrationOutput(Controller[Encodable]):
    """"""

    def __init__(self, serial_config: SerialConfig, parent: QObject | None = None) -> None:
        super().__init__(serial_config=serial_config, parent=parent)

        self._avg_timer = self.startTimer(1000, Qt.TimerType.CoarseTimer)

        self._avg_accumulator: list[tuple[int, int]] = []

    def timerEvent(self, event: QTimerEvent) -> None:
        if event.timerId() == self._avg_timer:
            if not self._avg_accumulator:
                return

            last_time, _ = self._avg_accumulator[-1]

            _keep = []
            for time, val in self._avg_accumulator:
                if time + 1000 > last_time:
                    _keep.append((time, val))

            self._avg_accumulator = _keep
