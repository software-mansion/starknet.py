from marshmallow import fields, post_load

from starknet_py.net.client_models import StarknetBlock
from starknet_py.net.schemas.common import BlockStatusField
from starknet_py.net.schemas.rpc.block_header import BlockHeaderSchema
from starknet_py.net.schemas.rpc.types_of_transactions import TypesOfTransactionsSchema


class StarknetBlockSchema(BlockHeaderSchema):
    status = BlockStatusField(data_key="status", required=True)
    transactions = fields.List(
        fields.Nested(TypesOfTransactionsSchema()),
        data_key="transactions",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> StarknetBlock:
        return StarknetBlock(**data)
