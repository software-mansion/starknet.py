from dataclasses import dataclass, field
from typing import Dict, Generator, List

from starknet_py.serialization import CairoDataSerializer
from starknet_py.serialization._context import (
    DeserializationContext,
    SerializationContext,
)


@dataclass
class OutputSerializer(CairoDataSerializer[List, List]):
    serializers: List[CairoDataSerializer] = field(init=True)

    def deserialize_with_context(self, context: DeserializationContext) -> List:
        result = []

        for serializer in self.serializers:
            with context.push_entity("output"):
                result.append(serializer.deserialize_with_context(context))

        return result

    def serialize_with_context(
        self, context: SerializationContext, value: Dict
    ) -> Generator[int, None, None]:
        pass
