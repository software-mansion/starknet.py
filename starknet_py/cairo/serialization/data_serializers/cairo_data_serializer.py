from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Generator

from starknet_py.cairo.serialization._serialization_context import SerializationContext
from starknet_py.cairo.serialization.errors import InvalidValueException

from starknet_py.cairo.serialization._calldata_reader import CalldataReader
from starknet_py.utils.data_transformer.data_transformer import CairoData

# Python type that is accepted by a transformer
# pylint: disable=invalid-name
SerializationType = TypeVar("SerializationType")

# Python type that will be returned from a transformer. Often same as SerializationType.
# pylint: disable=invalid-name
DeserializationType = TypeVar("DeserializationType")


class CairoDataSerializer(ABC, Generic[SerializationType, DeserializationType]):
    """
    Base class for serializing/deserializing data to/from calldata.
    """

    def deserialize(self, data: List[int]) -> DeserializationType:
        """
        Transform calldata into python value.

        :param data: calldata to deserialize.
        :return: defined DeserializationType.
        """
        reader = CalldataReader(data)
        result = self.deserialize_with_context(
            CalldataReader(data), SerializationContext()
        )
        if reader.remaining_len != 0:
            raise InvalidValueException(
                f"Provided {reader.remaining_len} excessive values out of total {len(data)} values for deserialization"
            )

        return result

    def serialize(self, data: SerializationType) -> CairoData:
        """
        Transform python data into calldata.

        :param data: data to serialize.
        :return: calldata.
        """
        return list(self.serialize_with_context(data, SerializationContext()))

    @abstractmethod
    def deserialize_with_context(
        self, reader: CalldataReader, context: SerializationContext
    ) -> DeserializationType:
        """
        Transform calldata into python value.

        :param reader: calldata reader.
        :param context: context of this transformation.
        :return: defined DeserializationType.
        """

    @abstractmethod
    def serialize_with_context(
        self, value: SerializationType, context: SerializationContext
    ) -> Generator[int, None, None]:
        """
        Transform python value into calldata.

        :param value: python value to transform.
        :param context: context of this transformation.
        :return: defined SerializationType.
        """
