import struct
from typing import cast, Self

from cobs import cobs  # type: ignore[import-untyped]
from pyside_app_core.constants import DATA_STRUCT_ENDIAN
from pyside_app_core.services.serial_service.types import ChunkedData, Decodable, Encodable, TranscoderInterface


class Message(Encodable):
    """"""

    def encode(self) -> bytes:
        return b""

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Result(Decodable):
    """"""

    def __init__(self, data: bytes):
        self._raw_data = data

    @classmethod
    def decode(cls, data: bytes) -> "Result":
        return cls(data)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>({self._raw_data!r})"


class CobsTranscoder(TranscoderInterface):
    """COBS transcoder"""

    @classmethod
    def process_buffer(cls, buffer: bytearray) -> ChunkedData:
        if b"\x00" in buffer:
            chunks: list[bytearray]
            remainder: bytearray
            *chunks, remainder = buffer.split(b"\x00")
            return chunks, remainder

        return [], None

    @classmethod
    def encode(cls, data: Encodable) -> bytes:
        return cast(bytes, cobs.encode(data.encode()))

    @classmethod
    def decode(cls, raw: bytearray) -> Result:
        return Result.decode(cobs.decode(raw))


class FloatResult(Decodable):
    """"""

    @property
    def value(self) -> float:
        return self._raw_data

    def __init__(self, data: float):
        self._raw_data = data

    @classmethod
    def decode(cls, data: bytes) -> Self:
        return cls(float(data))

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>({self.value})"


class LegacyTranscoder(TranscoderInterface):
    """legacy string transcoder"""

    SEP = b"\r\n"

    @classmethod
    def process_buffer(cls, buffer: bytearray) -> ChunkedData:
        if cls.SEP in buffer:
            chunks: list[bytearray]
            remainder: bytearray
            *chunks, remainder = buffer.split(cls.SEP)
            return chunks, remainder

        return [], None

    @classmethod
    def encode(cls, data: Encodable) -> bytes:
        return data.encode()

    @classmethod
    def decode(cls, raw: bytearray) -> FloatResult:
        return FloatResult.decode(raw)
