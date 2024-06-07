from marshmallow import fields, post_load

from starknet_py.net.client_models import InvokeTransactionV3
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.transaction_v3 import TransactionV3Schema


class InvokeTransactionV3Schema(TransactionV3Schema):
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    sender_address = Felt(data_key="sender_address", required=True)
    nonce = Felt(data_key="nonce", required=True)
    account_deployment_data = fields.List(
        Felt(), data_key="account_deployment_data", required=True
    )

    @post_load
    def make_transaction(self, data, **kwargs) -> InvokeTransactionV3:
        return InvokeTransactionV3(**data)
