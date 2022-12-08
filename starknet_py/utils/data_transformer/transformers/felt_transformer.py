# Just an integer or short string
from typing import Union

from starkware.crypto.signature.signature import FIELD_PRIME

from starknet_py.utils.data_transformer._calldata_reader import CalldataReader
from starknet_py.utils.data_transformer.data_transformer import CairoData

from starknet_py.cairo.felt import encode_shortstring, is_in_felt_range
from starknet_py.utils.data_transformer._transformation_context import (
    TransformationContext,
)
from starknet_py.utils.data_transformer.transformers.interface import Transformer

TransformableToFelt = Union[int, str]


class FeltTransformer(Transformer[TransformableToFelt, int]):
    def deserialize(
        self, context: TransformationContext, reader: CalldataReader
    ) -> int:
        [val] = reader.consume(1)
        self._assert_felt(context, val)
        return val

    def serialize(
        self, context: TransformationContext, value: TransformableToFelt
    ) -> CairoData:
        context.ensure_valid_type(isinstance(value, (int, str)), "int or short string")

        if isinstance(value, str):
            value = encode_shortstring(value)
            return [value]

        self._assert_felt(context, value)
        return [value]

    @staticmethod
    def _assert_felt(context: TransformationContext, value: int):
        context.ensure_valid_value(
            is_in_felt_range(value), f"value must be in [0, {FIELD_PRIME}) range"
        )
