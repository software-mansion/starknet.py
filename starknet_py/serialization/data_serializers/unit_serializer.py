from dataclasses import dataclass
from typing import Any, Generator, Optional

from starknet_py.serialization._context import (
    DeserializationContext,
    SerializationContext,
)
from starknet_py.serialization.data_serializers.cairo_data_serializer import (
    CairoDataSerializer,
)


# pyright: reportIncompatibleMethodOverride=false
@dataclass
class UnitSerializer(CairoDataSerializer[None, None]):
    """
    Serializer for unit type.
    Can only serialize None.
    Deserializes data to None.

    Example:
        [] => None
    """

    def deserialize_with_context(self, context: DeserializationContext) -> None:
        return None

    def serialize_with_context(
        self, context: SerializationContext, value: Optional[Any]
    ) -> Generator[None, None, None]:
        if value is not None:
            raise ValueError("Can only serialize `None`.")
        yield None
