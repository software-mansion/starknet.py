from dataclasses import dataclass
from typing import Generator

from starknet_py.constants import FIELD_PRIME
from starknet_py.serialization._context import (
    Context,
    DeserializationContext,
    SerializationContext,
)
from starknet_py.serialization.data_serializers.cairo_data_serializer import (
    CairoDataSerializer,
)


@dataclass
class IntSerializer(CairoDataSerializer[int, int]):
    """
    Serializer of int. In Cairo there are few ints (i8, ..., i64 and i128).
    Can serialize an int.
    Deserializes data to an int.
    """

    bits: int

    def deserialize_with_context(self, context: DeserializationContext) -> int:
        (raw,) = context.reader.read(1)

        signed_threshold = 1 << (self.bits - 1)
        deserialized_val = raw if raw < signed_threshold else raw - FIELD_PRIME
        with context.push_entity("int" + str(self.bits)):
            self._ensure_valid_int(
                deserialized_val,
                context,
                self.bits,
            )

            return deserialized_val

    def serialize_with_context(
        self, context: SerializationContext, value: int
    ) -> Generator[int, None, None]:
        context.ensure_valid_type(value, isinstance(value, int), "int")
        yield from self._serialize_from_int(value, context, self.bits)

    @staticmethod
    def _serialize_from_int(
        value: int, context: SerializationContext, bits: int
    ) -> Generator[int, None, None]:
        IntSerializer._ensure_valid_int(value, context, bits)

        unsigned = value % FIELD_PRIME

        yield unsigned

    @staticmethod
    def _ensure_valid_int(value: int, context: Context, bits: int):
        """
        Ensures that value is a valid int on `bits` bits.
        """
        min_val = -(1 << (bits - 1))
        max_val = (1 << (bits - 1)) - 1
        context.ensure_valid_value(
            (min_val <= value <= max_val),
            f"expected value in range [{min_val};{max_val}]",
        )
