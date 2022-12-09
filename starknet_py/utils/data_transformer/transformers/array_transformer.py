from dataclasses import dataclass
from typing import List

from starknet_py.utils.data_transformer._calldata_reader import CalldataReader
from starknet_py.utils.data_transformer._transformation_context import (
    TransformationContext,
)
from starknet_py.utils.data_transformer.data_transformer import CairoData
from starknet_py.utils.data_transformer.transformers.base_transformer import (
    BaseTransformer,
)


@dataclass
class ArrayTransformer(BaseTransformer[List, List]):
    inner_transformer: BaseTransformer

    def _deserialize(
        self, reader: CalldataReader, context: TransformationContext
    ) -> List:
        result = []

        with context.push_entity(f"len"):
            [size] = reader.read(1)

        for index in range(size):
            with context.push_entity(f"[{index}]"):
                transformed = self.inner_transformer._deserialize(reader, context)
                result.append(transformed)

        return result

    def _serialize(self, value: List, context: TransformationContext) -> CairoData:
        result = [len(value)]
        for index, value in enumerate(value):
            with context.push_entity(f"[{index}]"):
                transformed = self.inner_transformer._serialize(value, context)
                result.extend(transformed)

        return result
