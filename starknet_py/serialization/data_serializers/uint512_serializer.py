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
    low0: int
    low1: int
    high0: int
    high1: int


@dataclass
class Uint512Serializer(CairoDataSerializer[Union[int, Uint512Dict], int]):
    """
    Serializer of Uint512. In Cairo it is represented by structure {low0: Uint128, low1: Uint128, high0: Uint128, high1: Uint128}.
    Can serialize an int.
    Deserializes data to an int.

    Examples:
    0 => [0,0,0,0]
    1 => [1,0,0,0]
    2**128 => [0,1,0,0]
    2**256 => [0,0,1,0]
    2**384 => [0,0,0,1]
    3 + 2**128 => [3,1,0,0]
    """

    def deserialize_with_context(self, context: DeserializationContext) -> int:
        [low0, low1, high0, high1] = context.reader.read(4)

        # Checking if resulting value is in [0, 2**512) range is not enough. Uint512 should be made of four uint128.
        with context.push_entity("low0"):
            self._ensure_valid_uint128(low0, context)
        with context.push_entity("low1"):
            self._ensure_valid_uint128(low1, context)
        with context.push_entity("high0"):
            self._ensure_valid_uint128(high0, context)
        with context.push_entity("high1"):
            self._ensure_valid_uint128(high1, context)

        return (high1 << 384) + (high0 << 256) + (low1 << 128) + low0

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
        low0 = value % (2**128)
        low1 = (value >> 128) % (2**128)
        high0 = (value >> 256) % (2**128)
        high1 = (value >> 384) % (2**128)
        result = (low0, low1, high0, high1)
        yield from result

    def _serialize_from_dict(
        self, context: SerializationContext, value: Uint512Dict
    ) -> Generator[int, None, None]:
        with context.push_entity("low0"):
            self._ensure_valid_uint128(value["low0"], context)
            yield value["low0"]
        with context.push_entity("low1"):
            self._ensure_valid_uint128(value["low1"], context)
            yield value["low1"]
        with context.push_entity("high0"):
            self._ensure_valid_uint128(value["high0"], context)
            yield value["high0"]
        with context.push_entity("high1"):
            self._ensure_valid_uint128(value["high1"], context)
            yield value["high1"]

    @staticmethod
    def _ensure_valid_uint128(value: int, context: Context):
        context.ensure_valid_value(
            0 <= value < U128_UPPER_BOUND, "expected value in range [0;2**128)"
        )