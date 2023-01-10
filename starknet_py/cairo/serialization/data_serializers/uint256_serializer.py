from dataclasses import dataclass
from typing import Generator

from starknet_py.cairo.felt import uint256_range_check
from starknet_py.cairo.serialization._context import (
    DeserializationContext,
    SerializationContext,
)
from starknet_py.cairo.serialization.data_serializers.cairo_data_serializer import (
    CairoDataSerializer,
)

U128_UPPER_BOUND = 2**128


@dataclass
class Uint256Serializer(CairoDataSerializer[int, int]):
    """
    Serializer of Uint256. In Cairo it is represented by structure {low: Uint128, high: Uint128}.
    Can serialize an int.
    Deserializes data to an int.

    Examples:
    0 => [0,0]
    1 => [1,0]
    2**128 => [0,1]
    3 + 2**128 => [3,1]
    """

    def deserialize_with_context(self, context: DeserializationContext) -> int:
        [low, high] = context.reader.read(2)

        # Checking if resulting value is in [0, 2^256) range is not enough. Uint256 should be made of two uint128.
        with context.push_entity("low"):
            self._ensure_valid_uint128(low, context)
        with context.push_entity("high"):
            self._ensure_valid_uint128(high, context)

        return (high << 128) + low

    def serialize_with_context(
        self, context: SerializationContext, value: int
    ) -> Generator[int, None, None]:
        uint256_range_check(value)
        result = (value % 2**128, value // 2**128)
        yield from result

    @staticmethod
    def _ensure_valid_uint128(value: int, context: DeserializationContext):
        context.ensure_valid_value(
            0 <= value < U128_UPPER_BOUND, "expected value in range [0;2^128)"
        )
