from typing import Self, TypeVar

from cobs import cobs

from pyside_app_core.services.serial_service.types import ChunkedData, TranscoderInterface


class Command:
    """"""

    def encode(self) -> bytearray:
        return bytearray()

    def __str__(self) -> str:
        return "<Command> ..."


class Result:
    """"""

    def __init__(self, data: bytes):
        self._raw_data = data

    @classmethod
    def decode(cls, data: bytes) -> Self:
        return Result(data)

    def __str__(self) -> str:
        return "<Result> ..."


_TC = TypeVar("_TC", bound=Command)
_TR = TypeVar("_TR", bound=Result)


class CobsTranscoder(TranscoderInterface[_TC, _TR]):
    """ COBS transcoder """

    @classmethod
    def process_buffer(cls, buffer: bytearray) -> ChunkedData:
        if b"\x00" in buffer:
            chunks: list[bytearray]
            remainder: bytearray
            *chunks, remainder = buffer.split(b"\x00")
            return chunks, remainder

        return [], None

    @classmethod
    def encode(cls, data: _TC) -> bytearray:
        return cobs.encode(data.encode())

    @classmethod
    def decode(cls, raw: bytearray) -> _TR:
        return Result.decode(cobs.decode(raw))


class LegacyTranscoder(TranscoderInterface[_TC, _TR]):
    """ legacy string transcoder """

    @classmethod
    def process_buffer(cls, buffer: bytearray) -> ChunkedData:
        if b"\n" in buffer:
            chunks: list[bytearray]
            remainder: bytearray
            *chunks, remainder = buffer.split(b"\n")
            return chunks, remainder

        return [], None

    @classmethod
    def encode(cls, data: _TC) -> bytearray:
        return data.encode()

    @classmethod
    def decode(cls, raw: bytearray) -> _TR:
        return Result.decode(raw)
