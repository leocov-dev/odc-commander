import struct
from typing import Protocol, TypeVar

from odc_commander.commands.transcoder import Message

_V = TypeVar("_V")


class ParamType(Protocol[_V]):
    @property
    def value(self) -> _V: ...

    @value.setter
    def value(self, value: _V) -> None: ...

    @property
    def label(self) -> str: ...


class FloatParam(Message):
    def __init__(self, value: float, label: str) -> None:
        self._value = float(value)
        self._label = label

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = float(value)

    @property
    def label(self) -> str:
        return self._label

    def encode(self) -> bytes:
        return struct.pack(">f", self._value)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self._value:10.6f}>"
