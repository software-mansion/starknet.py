from marshmallow import post_load

from starknet_py.net.client_models import SentTransactionResponse
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class SentTransactionSchema(Schema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SentTransactionResponse:
        return SentTransactionResponse(**data)
