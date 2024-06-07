from marshmallow import fields, post_load

from starknet_py.net.client_models import InvokeTransactionV0
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.deprecated_transaction import (
    DeprecatedTransactionSchema,
)


class InvokeTransactionV0Schema(DeprecatedTransactionSchema):
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    contract_address = Felt(data_key="contract_address", required=True)
    entry_point_selector = Felt(data_key="entry_point_selector", required=True)

    @post_load
    def make_transaction(self, data, **kwargs) -> InvokeTransactionV0:
        return InvokeTransactionV0(**data)
