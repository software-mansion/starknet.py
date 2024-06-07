from marshmallow import fields, post_load

from starknet_py.net.client_models import L1HandlerTransactionTrace
from starknet_py.net.schemas.rpc.execution_resources import ExecutionResourcesSchema
from starknet_py.net.schemas.rpc.function_invocation import FunctionInvocationSchema
from starknet_py.net.schemas.rpc.state_diff import StateDiffSchema
from starknet_py.utils.schema import Schema


class L1HandlerTransactionTraceSchema(Schema):
    execution_resources = fields.Nested(
        ExecutionResourcesSchema(), data_key="execution_resources", required=True
    )

    function_invocation = fields.Nested(
        FunctionInvocationSchema(), data_key="function_invocation", required=True
    )
    state_diff = fields.Nested(
        StateDiffSchema(), data_key="state_diff", load_default=None
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> L1HandlerTransactionTrace:
        return L1HandlerTransactionTrace(**data)
