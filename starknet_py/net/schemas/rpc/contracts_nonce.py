from marshmallow import post_load

from starknet_py.net.client_models import ContractsNonce
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class ContractsNonceSchema(Schema):
    contract_address = Felt(data_key="contract_address", required=True)
    nonce = Felt(data_key="nonce", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return ContractsNonce(**data)
