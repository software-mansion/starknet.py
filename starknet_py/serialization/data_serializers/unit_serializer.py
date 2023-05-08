from dataclasses import dataclass
from typing import Generator, Union

from starknet_py.serialization import CairoDataSerializer
from starknet_py.serialization._context import (
    DeserializationContext,
    SerializationContext,
)
from starknet_py.serialization.data_serializers.uint256_serializer import Uint256Dict


@dataclass
class UnitSerializer(CairoDataSerializer[None, None]):
    """
    Serializer for unit type.
    Can't serialize anything.
    Deserializes data to None.

    Example:
        [] => None
    """

    def deserialize_with_context(self, context: DeserializationContext) -> None:
        return None

    def serialize_with_context(
        self, context: SerializationContext, value: Union[int, Uint256Dict]
    ) -> Generator[int, None, None]:  # pyright: ignore
        raise ValueError("Unit can't be serialized.")
