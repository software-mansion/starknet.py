from marshmallow import fields, post_load

from starknet_py.net.client_models import PendingStarknetBlockWithReceipts
from starknet_py.net.schemas.rpc.pending_block_header import PendingBlockHeaderSchema
from starknet_py.net.schemas.rpc.transaction_with_receipt import (
    TransactionWithReceiptSchema,
)


class PendingStarknetBlockWithReceiptsSchema(PendingBlockHeaderSchema):
    transactions = fields.List(
        fields.Nested(TransactionWithReceiptSchema()),
        data_key="transactions",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> PendingStarknetBlockWithReceipts:
        return PendingStarknetBlockWithReceipts(**data)
