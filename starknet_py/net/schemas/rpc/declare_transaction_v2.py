from marshmallow import post_load

from starknet_py.net.client_models import DeclareTransactionV2
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.deprecated_transaction import (
    DeprecatedTransactionSchema,
)


class DeclareTransactionV2Schema(DeprecatedTransactionSchema):
    sender_address = Felt(data_key="sender_address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)
    compiled_class_hash = Felt(data_key="compiled_class_hash", required=True)
    nonce = Felt(data_key="nonce", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransactionV2:
        return DeclareTransactionV2(**data)
