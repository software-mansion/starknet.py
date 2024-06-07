from marshmallow import post_load

from starknet_py.net.client_models import DeclareTransactionV0
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.deprecated_transaction import (
    DeprecatedTransactionSchema,
)


class DeclareTransactionV0Schema(DeprecatedTransactionSchema):
    sender_address = Felt(data_key="sender_address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransactionV0:
        return DeclareTransactionV0(**data)
