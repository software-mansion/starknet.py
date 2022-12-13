from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Union, List, Generator

from starknet_py.utils.data_transformer.errors import InvalidValueException

from starknet_py.utils.data_transformer._calldata_reader import CalldataReader
from starknet_py.utils.data_transformer.data_transformer import CairoData
from starknet_py.utils.data_transformer._transformation_context import (
    TransformationContext,
)

# Python type that is accepted by a transformer
SerializationType = TypeVar("SerializationType")

# Python type that will be returned from a transformer. Often same as SerializationType.
DeserializationType = TypeVar("DeserializationType")


class BaseTransformer(ABC, Generic[SerializationType, DeserializationType]):
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
        result = self._deserialize(CalldataReader(data), TransformationContext())
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
        return list(self._serialize(data, TransformationContext()))

    @abstractmethod
    def _deserialize(
        self, reader: CalldataReader, context: TransformationContext
    ) -> DeserializationType:
        """
        Transform calldata into python value.

        :param reader: calldata reader.
        :param context: context of this transformation.
        :return: defined DeserializationType.
        """
        pass

    @abstractmethod
    def _serialize(
        self, value: SerializationType, context: TransformationContext
    ) -> Generator[int, None, None]:
        """
        Transform python value into calldata.

        :param value: python value to transform.
        :param context: context of this transformation.
        :return: defined SerializationType.
        """
        pass
