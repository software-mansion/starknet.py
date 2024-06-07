from marshmallow import fields, post_load

from starknet_py.net.client_models import L1HandlerTransaction
from starknet_py.net.schemas.common import Felt, NumberAsHex
from starknet_py.net.schemas.rpc.transaction import TransactionSchema


class L1HandlerTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address", required=True)
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    entry_point_selector = Felt(data_key="entry_point_selector", required=True)
    nonce = NumberAsHex(data_key="nonce", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> L1HandlerTransaction:
        return L1HandlerTransaction(**data)
