from dataclasses import dataclass
from typing import Any, Generator

from starknet_py.serialization._context import (
    Context,
    DeserializationContext,
    SerializationContext,
)
from starknet_py.serialization.data_serializers.cairo_data_serializer import (
    CairoDataSerializer,
)


@dataclass
class NonZeroSerializer(CairoDataSerializer[Any, int]):
    """
    Serializer for NonZero type.
    Can serialize Cairo types which are non-zero.
    Deserializes data to int.
    """

    serializer: CairoDataSerializer

    def deserialize_with_context(self, context: DeserializationContext) -> int:
        deserialized_value = self.serializer.deserialize_with_context(context)
        self._ensure_valid_nonzero(deserialized_value, context)
        return deserialized_value

    def serialize_with_context(
        self,
        context: SerializationContext,
        value: Any,
    ) -> Generator[int, None, None]:
        self._ensure_valid_nonzero(value, context)
        return self.serializer.serialize_with_context(context, value)

    @staticmethod
    def _ensure_valid_nonzero(value: int, context: Context):
        context.ensure_valid_value(value != 0, "expected value to be non-zero")
