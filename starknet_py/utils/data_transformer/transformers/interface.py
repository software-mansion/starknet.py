from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from starknet_py.utils.data_transformer._calldata_reader import CalldataReader
from starknet_py.utils.data_transformer.data_transformer import CairoData
from starknet_py.utils.data_transformer._transformation_context import (
    TransformationContext,
)

# Python type that is accepted by a transformer
SerializationType = TypeVar("SerializationType")

# Python type that will be returned from a transformer. Often same as AcceptedPythonType.
DeserializationType = TypeVar("DeserializationType")


class Transformer(ABC, Generic[SerializationType, DeserializationType]):
    """
    Interface for serializing/deserializing data to/from calldata.
    """

    @abstractmethod
    def deserialize(
        self, context: TransformationContext, reader: CalldataReader
    ) -> DeserializationType:
        """
        Transform calldata into python value.

        :param context: context of this transformation.
        :param reader: calldata reader.
        :return: defined DeserializationType.
        """
        pass

    @abstractmethod
    def serialize(
        self, context: TransformationContext, value: SerializationType
    ) -> CairoData:
        """
        Transform python value into calldata.

        :param context: context of this transformation.
        :param value: python value to transform.
        :return: defined SerializationType.
        """
        pass
