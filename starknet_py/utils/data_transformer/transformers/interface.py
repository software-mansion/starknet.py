from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from starknet_py.utils.data_transformer._data_reader import CalldataReader
from starknet_py.utils.data_transformer.data_transformer import CairoData
from starknet_py.utils.data_transformer.types.CairoType import TransformContext

# Python type that is accepted by a transformer
SerializationType = TypeVar("SerializationType")

# Python type that will be returned from a transformer. Often same as AcceptedPythonType.
DeserializationType = TypeVar("DeserializationType")


class Transformer(ABC, Generic[SerializationType, DeserializationType]):
    @abstractmethod
    def deserialize(
        self, context: TransformContext, reader: CalldataReader
    ) -> DeserializationType:
        pass

    @abstractmethod
    def serialize(
        self, context: TransformContext, value: SerializationType
    ) -> CairoData:
        pass
