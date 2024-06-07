from marshmallow import fields, post_load

from starknet_py.net.client_models import PendingStarknetBlockWithTxHashes
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.pending_block_header import PendingBlockHeaderSchema


class PendingStarknetBlockWithTxHashesSchema(PendingBlockHeaderSchema):
    transactions = fields.List(Felt(), data_key="transactions", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> PendingStarknetBlockWithTxHashes:
        return PendingStarknetBlockWithTxHashes(**data)
