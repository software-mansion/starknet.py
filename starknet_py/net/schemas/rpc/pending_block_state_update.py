from marshmallow import fields, post_load

from starknet_py.net.client_models import PendingBlockStateUpdate
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.state_diff import StateDiffSchema
from starknet_py.utils.schema import Schema


class PendingBlockStateUpdateSchema(Schema):
    old_root = Felt(data_key="old_root", required=True)
    state_diff = fields.Nested(StateDiffSchema(), data_key="state_diff", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> PendingBlockStateUpdate:
        return PendingBlockStateUpdate(**data)
