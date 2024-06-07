from marshmallow import post_load

from starknet_py.net.client_models import DeployedContract
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class ContractDiffSchema(Schema):
    address = Felt(data_key="address", required=True)
    contract_hash = Felt(data_key="contract_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployedContract:
        return DeployedContract(**data)
