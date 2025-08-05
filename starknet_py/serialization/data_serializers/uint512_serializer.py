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
    limb0: int
    limb1: int
    limb2: int
    limb3: int


@dataclass
class Uint512Serializer(CairoDataSerializer[Union[int, Uint512Dict], int]):
    """
    Serializer of Uint512. In Cairo it is represented by structure {limb0: Uint128, limb1: Uint128, limb2: Uint128, limb3: Uint128}.
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
        [limb0, limb1, limb2, limb3] = context.reader.read(4)

        # Checking if resulting value is in [0, 2**512) range is not enough. Uint512 should be made of four uint128.
        with context.push_entity("limb0"):
            self._ensure_valid_uint128(limb0, context)
        with context.push_entity("limb1"):
            self._ensure_valid_uint128(limb1, context)
        with context.push_entity("limb2"):
            self._ensure_valid_uint128(limb2, context)
        with context.push_entity("limb3"):
            self._ensure_valid_uint128(limb3, context)

        return (limb3 << 384) + (limb2 << 256) + (limb1 << 128) + limb0

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
        limb0 = value % (2**128)
        limb1 = (value >> 128) % (2**128)
        limb2 = (value >> 256) % (2**128)
        limb3 = (value >> 384) % (2**128)
        result = (limb0, limb1, limb2, limb3)
        yield from result

    def _serialize_from_dict(
        self, context: SerializationContext, value: Uint512Dict
    ) -> Generator[int, None, None]:
        with context.push_entity("limb0"):
            self._ensure_valid_uint128(value["limb0"], context)
            yield value["limb0"]
        with context.push_entity("limb1"):
            self._ensure_valid_uint128(value["limb1"], context)
            yield value["limb1"]
        with context.push_entity("limb2"):
            self._ensure_valid_uint128(value["limb2"], context)
            yield value["limb2"]
        with context.push_entity("limb3"):
            self._ensure_valid_uint128(value["limb3"], context)
            yield value["limb3"]

    @staticmethod
    def _ensure_valid_uint128(value: int, context: Context):
        context.ensure_valid_value(
            0 <= value < U128_UPPER_BOUND, "expected value in range [0;2**128)"
        )