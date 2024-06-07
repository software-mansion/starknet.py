from marshmallow import EXCLUDE, fields, post_load

from starknet_py.net.client_models import BlockTransactionTrace
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.transaction_trace import TransactionTraceSchema
from starknet_py.utils.schema import Schema


class BlockTransactionTraceSchema(Schema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)
    # `unknown=EXCLUDE` in order to skip `type=...` field we don't want
    trace_root = fields.Nested(
        TransactionTraceSchema(), data_key="trace_root", required=True, unknown=EXCLUDE
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> BlockTransactionTrace:
        return BlockTransactionTrace(**data)
