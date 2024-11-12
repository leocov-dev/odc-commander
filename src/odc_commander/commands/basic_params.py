import struct
from collections.abc import Iterable, MutableSequence
from typing import Any, overload, Protocol, TypeVar, Self

from pydantic import BaseModel, Field, model_validator
from pyside_app_core.constants import DATA_ENCODING_ENDIAN, DATA_STRUCT_ENDIAN

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
    value: float = Field()
    default: float
    label: str
    unit: str = ""
    step: float = 0.1
    min_value: float
    max_value: float
    decimals: int = 2

    @model_validator(mode="before")
    @classmethod
    def _apply_default(cls, data: dict[str, Any]):
        if "value" not in data:
            data["value"] = data.get("default", 0.0)
        if "min_value" not in data:
            data["min_value"] = data.get("default", 0.0)
        if "max_value" not in data:
            data["max_value"] = data.get("default", 10.0) * 2

        return data

    @model_validator(mode="after")
    def _clamp_value(self) -> Self:
        self.value = max(self.min_value, min(self.max_value, self.value))
        self.default = max(self.min_value, min(self.max_value, self.default))
        return self

    def reset(self) -> None:
        self.value = self.default

    def encode(self) -> bytes:
        return struct.pack(">f", self.value)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {super().__str__()}>"


class FloatArrayParam(ParamType[list[float]], Message, MutableSequence[FloatParam]):
    def __init__(self, *floats: FloatParam):
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
        return struct.pack(f"{DATA_STRUCT_ENDIAN}{fmt}", *self.value)

    def __str__(self) -> str:
        str_vals = [f"{v:.6f}" for v in self.value]
        return f"<{self.__class__.__name__}: [{', '.join(str_vals)}]> {self.encode()}"
