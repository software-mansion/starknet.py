from dataclasses import dataclass
from typing import Optional, Any

from starknet_py.serialization import CairoDataSerializer
from starknet_py.serialization._context import DeserializationContext


@dataclass
class OptionSerializer(CairoDataSerializer[Optional[Any], Optional[Any]]):
    serializer: CairoDataSerializer

    def deserialize_with_context(
        self, context: DeserializationContext
    ) -> Optional[Any]:
        return self.serializer.deserialize_with_context(context)
