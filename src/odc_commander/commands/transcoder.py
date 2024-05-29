from typing import cast

from cobs import cobs  # type: ignore[import-untyped]
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

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>"


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


class LegacyTranscoder(TranscoderInterface):
    """legacy string transcoder"""

    @classmethod
    def process_buffer(cls, buffer: bytearray) -> ChunkedData:
        if b"\n" in buffer:
            chunks: list[bytearray]
            remainder: bytearray
            *chunks, remainder = buffer.split(b"\n")
            return chunks, remainder

        return [], None

    @classmethod
    def encode(cls, data: Encodable) -> bytes:
        return data.encode()

    @classmethod
    def decode(cls, raw: bytearray) -> Result:
        return Result.decode(raw)
