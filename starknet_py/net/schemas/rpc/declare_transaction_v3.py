from marshmallow import fields, post_load

from starknet_py.net.client_models import DeclareTransactionV3
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.transaction_v3 import TransactionV3Schema


class DeclareTransactionV3Schema(TransactionV3Schema):
    sender_address = Felt(data_key="sender_address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)

    compiled_class_hash = Felt(data_key="compiled_class_hash", required=True)
    nonce = Felt(data_key="nonce", required=True)
    account_deployment_data = fields.List(
        Felt(), data_key="account_deployment_data", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransactionV3:
        return DeclareTransactionV3(**data)
