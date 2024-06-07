from marshmallow import fields, post_load

from starknet_py.net.client_models import BlockHashAndNumber
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class BlockHashAndNumberSchema(Schema):
    block_hash = Felt(data_key="block_hash", required=True)
    block_number = fields.Integer(data_key="block_number", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> BlockHashAndNumber:
        return BlockHashAndNumber(**data)
