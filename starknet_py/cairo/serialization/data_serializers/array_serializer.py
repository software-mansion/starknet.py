from dataclasses import dataclass
from typing import List, Generator, Iterable

from starknet_py.cairo.serialization._context import (
    DeserializationContext,
    SerializationContext,
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
        result = []

        with context.push_entity("len"):
            [size] = context.reader.read(1)

        for index in range(size):
            with context.push_entity(f"[{index}]"):
                result.append(self.inner_serializer.deserialize_with_context(context))

        return result

    def serialize_with_context(
        self, context: SerializationContext, value: List
    ) -> Generator[int, None, None]:
        yield len(value)
        for index, element in enumerate(value):
            with context.push_entity(f"[{index}]"):
                yield from self.inner_serializer.serialize_with_context(
                    context, element
                )
