from marshmallow import post_load

from starknet_py.net.client_models import DeployedContract
from starknet_py.net.schemas.common import Felt, NonPrefixedHex
from starknet_py.utils.schema import Schema


class DeployedContractSchema(Schema):
    address = Felt(data_key="address", required=True)
    class_hash = NonPrefixedHex(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return DeployedContract(**data)
