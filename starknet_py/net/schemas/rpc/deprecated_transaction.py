from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.transaction import TransactionSchema


class DeprecatedTransactionSchema(TransactionSchema):
    max_fee = Felt(data_key="max_fee", required=True)
