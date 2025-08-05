from dataclasses import dataclass
from typing import Generator, TypedDict, Union

from starknet_py.cairo.felt import uint512_range_check
from starknet_py.serialization._context import (
    Context,
    DeserializationContext,
    SerializationContext,
)
from starknet_py.serialization.data_serializers.cairo_data_serializer import (
    CairoDataSerializer,
)

U128_UPPER_BOUND = 2**128


class Uint512Dict(TypedDict):
    d0: int
    d1: int
    d2: int
    d3: int


@dataclass
class Uint512Serializer(CairoDataSerializer[Union[int, Uint512Dict], int]):
    """
    Serializer of Uint512. In Cairo it is represented by structure {d0: Uint128, d1: Uint128, d2: Uint128, d3: Uint128}.
    Can serialize an int.
    Deserializes data to an int.

    Examples:
    0 => [0,0,0,0]
    1 => [1,0,0,0]
    2**128 => [0,1,0,0]
    3 + 2**128 => [3,1,0,0]
    2**256 => [0,0,1,0]
    2**384 => [0,0,0,1]
    """

    def deserialize_with_context(self, context: DeserializationContext) -> int:
        [d0, d1, d2, d3] = context.reader.read(4)

        # Checking if resulting value is in [0, 2**512) range is not enough. Uint512 should be made of four uint128.
        with context.push_entity("d0"):
            self._ensure_valid_uint128(d0, context)
        with context.push_entity("d1"):
            self._ensure_valid_uint128(d1, context)
        with context.push_entity("d2"):
            self._ensure_valid_uint128(d2, context)
        with context.push_entity("d3"):
            self._ensure_valid_uint128(d3, context)

        return d0 + (d1 << 128) + (d2 << 256) + (d3 << 384)

    def serialize_with_context(
        self, context: SerializationContext, value: Union[int, Uint512Dict]
    ) -> Generator[int, None, None]:
        context.ensure_valid_type(value, isinstance(value, (int, dict)), "int or dict")
        if isinstance(value, int):
            yield from self._serialize_from_int(value)
        else:
            yield from self._serialize_from_dict(context, value)

    @staticmethod
    def _serialize_from_int(value: int) -> Generator[int, None, None]:
        uint512_range_check(value)
        d0 = value % (1 << 128)
        d1 = (value >> 128) % (1 << 128)
        d2 = (value >> 256) % (1 << 128)
        d3 = (value >> 384) % (1 << 128)
        yield d0
        yield d1
        yield d2
        yield d3

    def _serialize_from_dict(
        self, context: SerializationContext, value: Uint512Dict
    ) -> Generator[int, None, None]:
        with context.push_entity("d0"):
            self._ensure_valid_uint128(value["d0"], context)
            yield value["d0"]
        with context.push_entity("d1"):
            self._ensure_valid_uint128(value["d1"], context)
            yield value["d1"]
        with context.push_entity("d2"):
            self._ensure_valid_uint128(value["d2"], context)
            yield value["d2"]
        with context.push_entity("d3"):
            self._ensure_valid_uint128(value["d3"], context)
            yield value["d3"]

    @staticmethod
    def _ensure_valid_uint128(value: int, context: Context):
        context.ensure_valid_value(
            0 <= value < U128_UPPER_BOUND, "expected value in range [0;2**128)"
        )