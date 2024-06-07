from marshmallow import fields, post_load

from starknet_py.net.client_models import DeployAccountTransactionV1
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.deprecated_transaction import (
    DeprecatedTransactionSchema,
)


class DeployAccountTransactionV1Schema(DeprecatedTransactionSchema):
    nonce = Felt(data_key="nonce", required=True)
    contract_address_salt = Felt(data_key="contract_address_salt", required=True)
    constructor_calldata = fields.List(
        Felt(), data_key="constructor_calldata", required=True
    )
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployAccountTransactionV1:
        return DeployAccountTransactionV1(**data)
