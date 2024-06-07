from marshmallow import post_load

from starknet_py.net.client_models import TransactionStatus
from starknet_py.net.schemas.common import ExecutionStatusField, StatusField
from starknet_py.utils.schema import Schema


class TransactionStatusResponseSchema(Schema):
    finality_status = StatusField(data_key="finality_status", required=True)
    execution_status = ExecutionStatusField(
        data_key="execution_status", load_default=None
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionStatus:
        return TransactionStatus(**data)
