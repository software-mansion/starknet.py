from typing import Union, Generator

from starkware.crypto.signature.signature import FIELD_PRIME

from starknet_py.cairo.serialization._calldata_reader import CalldataReader

from starknet_py.cairo.felt import encode_shortstring, is_in_felt_range
from starknet_py.cairo.serialization._serialization_context import (
    SerializationContext,
)

from starknet_py.cairo.serialization.data_serializers.cairo_data_serializer import (
    CairoDataSerializer,
)


# Just an integer or short string
TransformableToFelt = Union[int, str]


class FeltSerializer(CairoDataSerializer[TransformableToFelt, int]):
    def deserialize_with_context(
        self, reader: CalldataReader, context: SerializationContext
    ) -> int:
        [val] = reader.read(1)
        self._ensure_felt(context, val)
        return val

    def serialize_with_context(
        self, value: TransformableToFelt, context: SerializationContext
    ) -> Generator[int, None, None]:
        context.ensure_valid_type(isinstance(value, (int, str)), "int or short string")

        if isinstance(value, str):
            value = encode_shortstring(value)
            yield value
        else:
            self._ensure_felt(context, value)
            yield value

    @staticmethod
    def _ensure_felt(context: SerializationContext, value: int):
        context.ensure_valid_value(
            is_in_felt_range(value), f"value must be in [0, {FIELD_PRIME}) range"
        )
