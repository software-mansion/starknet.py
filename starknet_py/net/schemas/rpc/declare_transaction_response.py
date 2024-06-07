from marshmallow import post_load

from starknet_py.net.client_models import DeclareTransactionResponse
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.sent_transaction import SentTransactionSchema


class DeclareTransactionResponseSchema(SentTransactionSchema):
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransactionResponse:
        return DeclareTransactionResponse(**data)
