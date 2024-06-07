from marshmallow import EXCLUDE, fields, post_load

from starknet_py.net.client_models import SimulatedTransaction
from starknet_py.net.schemas.rpc.estimated_fee import EstimatedFeeSchema
from starknet_py.net.schemas.rpc.transaction_trace import TransactionTraceSchema
from starknet_py.utils.schema import Schema


class SimulatedTransactionSchema(Schema):
    # `unknown=EXCLUDE` in order to skip `type=...` field we don't want
    transaction_trace = fields.Nested(
        TransactionTraceSchema(),
        data_key="transaction_trace",
        required=True,
        unknown=EXCLUDE,
    )
    fee_estimation = fields.Nested(
        EstimatedFeeSchema(), data_key="fee_estimation", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> SimulatedTransaction:
        return SimulatedTransaction(**data)
