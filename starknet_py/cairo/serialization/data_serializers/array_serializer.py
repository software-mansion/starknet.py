from dataclasses import dataclass
from typing import List, Generator, Iterable

from starknet_py.cairo.serialization._context import (
    DeserializationContext,
    SerializationContext,
)
from starknet_py.cairo.serialization.data_serializers._common import (
    deserialize_to_list,
    serialize_from_list,
)
from starknet_py.cairo.serialization.data_serializers.cairo_data_serializer import (
    CairoDataSerializer,
)


@dataclass
class ArraySerializer(CairoDataSerializer[Iterable, List]):
    """
    Serializer for arrays. In abi they are represented as a pointer to a type.
    Can serialize any iterable.
    Deserializes data to a TupleDataclass.
    """

    inner_serializer: CairoDataSerializer

    def deserialize_with_context(self, context: DeserializationContext) -> List:
        with context.push_entity("len"):
            [size] = context.reader.read(1)

        return deserialize_to_list([self.inner_serializer] * size, context)

    def serialize_with_context(
        self, context: SerializationContext, value: List
    ) -> Generator[int, None, None]:
        yield len(value)
        yield from serialize_from_list(
            [self.inner_serializer] * len(value), context, value
        )
