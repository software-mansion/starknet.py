from marshmallow import fields, post_load

from starknet_py.net.client_models import BlockStateUpdate
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.state_diff import StateDiffSchema
from starknet_py.utils.schema import Schema


class BlockStateUpdateSchema(Schema):
    block_hash = Felt(data_key="block_hash", required=True)
    new_root = Felt(data_key="new_root", required=True)
    old_root = Felt(data_key="old_root", required=True)
    state_diff = fields.Nested(StateDiffSchema(), data_key="state_diff", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> BlockStateUpdate:
        return BlockStateUpdate(**data)
