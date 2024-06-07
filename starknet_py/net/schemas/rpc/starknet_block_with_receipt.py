from marshmallow import fields, post_load

from starknet_py.net.client_models import StarknetBlockWithReceipts
from starknet_py.net.schemas.common import BlockStatusField
from starknet_py.net.schemas.rpc.block_header import BlockHeaderSchema
from starknet_py.net.schemas.rpc.transaction_with_receipt import (
    TransactionWithReceiptSchema,
)


class StarknetBlockWithReceiptsSchema(BlockHeaderSchema):
    status = BlockStatusField(data_key="status", required=True)
    transactions = fields.List(
        fields.Nested(TransactionWithReceiptSchema()),
        data_key="transactions",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> StarknetBlockWithReceipts:
        return StarknetBlockWithReceipts(**data)
