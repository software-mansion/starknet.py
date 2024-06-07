from marshmallow import post_load

from starknet_py.net.client_models import DeclareTransactionV1
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.deprecated_transaction import (
    DeprecatedTransactionSchema,
)


class DeclareTransactionV1Schema(DeprecatedTransactionSchema):
    sender_address = Felt(data_key="sender_address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)
    nonce = Felt(data_key="nonce", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransactionV1:
        return DeclareTransactionV1(**data)
