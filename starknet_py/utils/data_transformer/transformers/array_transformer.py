from dataclasses import dataclass
from typing import List

from starknet_py.utils.data_transformer._calldata_reader import CalldataReader
from starknet_py.utils.data_transformer._transformation_context import (
    TransformationContext,
)
from starknet_py.utils.data_transformer.data_transformer import CairoData
from starknet_py.utils.data_transformer.transformers.interface import Transformer


@dataclass
class ArrayTransformer(Transformer[List, List]):
    inner_transformer: Transformer

    def deserialize(
        self, context: TransformationContext, reader: CalldataReader
    ) -> List:
        result = []

        with context.nest(f"len"):
            [size] = reader.consume(1)

        for index in range(size):
            with context.nest(f"[{index}]"):
                transformed = self.inner_transformer.deserialize(context, reader)
                result.append(transformed)

        return result

    def serialize(self, context: TransformationContext, value: List) -> CairoData:
        result = [len(value)]
        for index, value in enumerate(List):
            with context.nest(f"[{index}]"):
                transformed = self.inner_transformer.serialize(context, value[index])
                result.extend(transformed)

        return result
