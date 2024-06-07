from marshmallow import fields, post_load

from starknet_py.net.client_models import InvokeTransactionV1
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.deprecated_transaction import (
    DeprecatedTransactionSchema,
)


class InvokeTransactionV1Schema(DeprecatedTransactionSchema):
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    sender_address = Felt(data_key="sender_address", required=True)
    nonce = Felt(data_key="nonce", required=True)

    @post_load
    def make_transaction(self, data, **kwargs) -> InvokeTransactionV1:
        return InvokeTransactionV1(**data)
