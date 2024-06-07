from marshmallow import post_load

from starknet_py.net.client_models import DeployAccountTransactionResponse
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.sent_transaction import SentTransactionSchema


class DeployAccountTransactionResponseSchema(SentTransactionSchema):
    address = Felt(data_key="contract_address", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployAccountTransactionResponse:
        return DeployAccountTransactionResponse(**data)
