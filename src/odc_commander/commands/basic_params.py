import struct
from collections.abc import MutableSequence
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


class FloatParam(ParamType[float], Message):
    def __init__(
        self,
        value: float,
        label: str,
        unit: str = "",
        step: float = 0.1,
        min_value: float = -1000.0,
        max_value: float = 1000.0,
    ) -> None:
        self._value = float(value)
        self._label = label
        self._unit = unit
        self._step = step
        self._min_value = min_value
        self._max_value = max_value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = max(self.min_value, min(self.max_value, float(value)))

    @property
    def label(self) -> str:
        return self._label

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def step(self) -> float:
        return self._step

    @property
    def min_value(self) -> float:
        return self._min_value

    @property
    def max_value(self) -> float:
        return self._max_value

    def encode(self) -> bytes:
        return struct.pack(">f", self.value)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.value:10.6f}>"


class FloatArrayParam(ParamType[list[float]], Message, MutableSequence[FloatParam]):

    def __init__(self, *floats: FloatParam):
        self._floats = list(floats or ())

    def __getitem__(self, index: int) -> FloatParam:
        return self.params[index]

    def __setitem__(self, index: int, value: FloatParam) -> None:
        self.params[index] = value

    def __delitem__(self, index: int) -> None:
        del self.params[index]

    def __len__(self):
        return len(self.params)

    def insert(self, index: int, value: FloatParam) -> None:
        self.params.insert(index, value)

    @property
    def params(self) -> list[FloatParam]:
        return self._floats

    @property
    def value(self) -> list[float]:
        return [f.value for f in self.params]

    @value.setter
    def value(self, value: list[float]) -> None:
        for i, f in enumerate(value):
            self._floats[i].value = f

    def encode(self) -> bytes:
        fmt = "f" * len(self.params)
        return struct.pack(f">{fmt}", *self.value)

    def __str__(self) -> str:
        str_vals = [f"{v:10.6f}" for v in self.value]
        return f"<{self.__class__.__name__}: [{', '.join(str_vals)}]>"
