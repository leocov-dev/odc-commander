import struct
from collections.abc import Iterable, MutableSequence
from typing import overload, Protocol, TypeVar, Self

from pydantic import BaseModel, model_validator

from odc_commander.commands.transcoder import Message

_V = TypeVar("_V")


class ParamType(Protocol[_V]):
    @property
    def value(self) -> _V: ...

    @value.setter
    def value(self, value: _V) -> None: ...

    @property
    def label(self) -> str: ...


class FloatParam(BaseModel):
    value: float
    label: str
    unit: str = ""
    step: float = 0.1
    min_value: float = -1000.0
    max_value: float = 1000.0

    @model_validator(mode="after")
    def _clamp_value(self) -> Self:
        self.value = max(self.min_value, min(self.max_value, float(self.value)))
        return self

    def encode(self) -> bytes:
        return struct.pack(">f", self.value)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.value:10.6f}>"


class FloatArrayParam(ParamType[list[float]], Message, MutableSequence[FloatParam]):
    def __init__(self, label: str, *floats: FloatParam):
        self._label = label
        self._floats = list(floats or ())

    @overload
    def __getitem__(self, index: int) -> FloatParam: ...

    @overload
    def __getitem__(self, index: slice) -> MutableSequence[FloatParam]: ...

    def __getitem__(self, index: int | slice) -> FloatParam | MutableSequence[FloatParam]:
        return self._floats[index]

    @overload
    def __setitem__(self, index: int, value: FloatParam) -> None: ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[FloatParam]) -> None: ...

    def __setitem__(self, index: int | slice, value: FloatParam | Iterable[FloatParam]) -> None:
        self.params[index] = value  # type: ignore[index, assignment]

    @overload
    def __delitem__(self, index: int) -> None: ...

    @overload
    def __delitem__(self, index: slice) -> None: ...

    def __delitem__(self, index: int | slice) -> None:
        del self.params[index]

    def __len__(self) -> int:
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

    @property
    def label(self) -> str:
        return ""

    def encode(self) -> bytes:
        fmt = "f" * len(self.params)
        return struct.pack(f">{fmt}", *self.value)

    def __str__(self) -> str:
        str_vals = [f"{v:10.6f}" for v in self.value]
        return f"<{self.__class__.__name__}: [{', '.join(str_vals)}]>"
