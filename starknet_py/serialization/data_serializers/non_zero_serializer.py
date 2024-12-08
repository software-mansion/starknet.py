import copy
from dataclasses import dataclass
from typing import Generator, Union

from starknet_py.serialization._context import (
    Context,
    DeserializationContext,
    SerializationContext,
)
from starknet_py.serialization.data_serializers.cairo_data_serializer import (
    CairoDataSerializer,
)
from starknet_py.serialization.data_serializers.felt_serializer import FeltSerializer
from starknet_py.serialization.data_serializers.uint256_serializer import (
    Uint256Dict,
    Uint256Serializer,
)
from starknet_py.serialization.data_serializers.uint_serializer import UintSerializer


@dataclass
class NonZeroSerializer(CairoDataSerializer[Union[int, Uint256Dict], int]):
    """
    Serializer for NonZero type.
    Can serialize Cairo numeric types which are non-zero.
    Deserializes data to int.
    """

    serializer: Union[UintSerializer, Uint256Serializer, FeltSerializer]

    def deserialize_with_context(self, context: DeserializationContext) -> int:
        reader_copy = copy.deepcopy(context.reader)
        if context.reader.remaining_len == 1:
            (value,) = reader_copy.read(1)
            self._ensure_valid_nonzero(value, context)
        elif context.reader.remaining_len == 2:
            [low, high] = reader_copy.read(2)
            self._ensure_valid_nonzero({"low": low, "high": high}, context)
        else:
            raise ValueError(
                f"Expected 1 or 2 elements for numeric type, got {context.reader.remaining_len}"
            )

        return self.serializer.deserialize_with_context(context)

    def serialize_with_context(
        self, context: SerializationContext, value: Union[int, Uint256Dict]
    ) -> Generator[int, None, None]:
        self._ensure_valid_nonzero(value, context)

        if isinstance(value, dict):
            if not isinstance(self.serializer, (UintSerializer, Uint256Serializer)):
                raise ValueError(
                    f"Expected serializer to be UintSerializer or Uint256Serializer, got {self.serializer.__class__.__name__}"
                )
            return self.serializer.serialize_with_context(context, value)

        return self.serializer.serialize_with_context(context, value)

    @staticmethod
    def _ensure_valid_nonzero(value: Union[int, Uint256Dict], context: Context):
        if isinstance(value, int):
            context.ensure_valid_value(value != 0, "expected value to be non-zero")
        elif isinstance(value, dict):
            context.ensure_valid_value(
                value["low"] != 0 or value["high"] != 0,
                "expected value to be non-zero",
            )
