# Just an integer or short string
from typing import Union

from starkware.crypto.signature.signature import FIELD_PRIME

from starknet_py.utils.data_transformer._calldata_reader import CalldataReader
from starknet_py.utils.data_transformer.data_transformer import CairoData

from starknet_py.cairo.felt import encode_shortstring, is_in_felt_range
from starknet_py.utils.data_transformer._transformation_context import (
    TransformationContext,
)
from starknet_py.utils.data_transformer.transformers.base_transformer import (
    BaseTransformer,
)

TransformableToFelt = Union[int, str]


class FeltTransformer(BaseTransformer[TransformableToFelt, int]):
    def _deserialize(
        self, reader: CalldataReader, context: TransformationContext
    ) -> int:
        [val] = reader.read(1)
        self._ensure_felt(context, val)
        return val

    def _serialize(
        self, value: TransformableToFelt, context: TransformationContext
    ) -> CairoData:
        context.ensure_valid_type(isinstance(value, (int, str)), "int or short string")

        if isinstance(value, str):
            value = encode_shortstring(value)
            return [value]

        self._ensure_felt(context, value)
        return [value]

    @staticmethod
    def _ensure_felt(context: TransformationContext, value: int):
        context.ensure_valid_value(
            is_in_felt_range(value), f"value must be in [0, {FIELD_PRIME}) range"
        )
