from dataclasses import dataclass
from typing import List, Generator

from starknet_py.cairo.serialization._calldata_reader import CalldataReader

from starknet_py.cairo.serialization._serialization_context import SerializationContext
from starknet_py.cairo.serialization.data_serializers.cairo_data_serializer import (
    CairoDataSerializer,
)


@dataclass
class ArraySerializer(CairoDataSerializer[List, List]):
    inner_transformer: CairoDataSerializer

    def deserialize_with_context(
        self, reader: CalldataReader, context: SerializationContext
    ) -> List:
        result = []

        with context.push_entity("len"):
            [size] = reader.read(1)

        for index in range(size):
            with context.push_entity(f"[{index}]"):
                transformed = self.inner_transformer.deserialize_with_context(
                    reader, context
                )
                result.append(transformed)

        return result

    def serialize_with_context(
        self, value: List, context: SerializationContext
    ) -> Generator[int, None, None]:
        yield len(value)
        for index, element in enumerate(value):
            with context.push_entity(f"[{index}]"):
                yield from self.inner_transformer.serialize_with_context(
                    element, context
                )
