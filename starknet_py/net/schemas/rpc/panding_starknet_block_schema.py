from marshmallow import fields, post_load

from starknet_py.net.client_models import PendingStarknetBlock
from starknet_py.net.schemas.rpc.pending_block_header import PendingBlockHeaderSchema
from starknet_py.net.schemas.rpc.types_of_transactions import TypesOfTransactionsSchema


class PendingStarknetBlockSchema(PendingBlockHeaderSchema):
    transactions = fields.List(
        fields.Nested(TypesOfTransactionsSchema()),
        data_key="transactions",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> PendingStarknetBlock:
        return PendingStarknetBlock(**data)
