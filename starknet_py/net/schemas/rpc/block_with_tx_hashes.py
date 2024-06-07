from marshmallow import fields, post_load

from starknet_py.net.client_models import StarknetBlockWithTxHashes
from starknet_py.net.schemas.common import BlockStatusField, Felt
from starknet_py.net.schemas.rpc.block_header import BlockHeaderSchema


class StarknetBlockWithTxHashesSchema(BlockHeaderSchema):
    status = BlockStatusField(data_key="status", required=True)
    transactions = fields.List(Felt(), data_key="transactions", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> StarknetBlockWithTxHashes:
        return StarknetBlockWithTxHashes(**data)
