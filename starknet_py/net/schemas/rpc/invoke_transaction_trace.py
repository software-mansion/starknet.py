from marshmallow import fields, post_load

from starknet_py.net.client_models import InvokeTransactionTrace
from starknet_py.net.schemas.rpc.execute_invocation import ExecuteInvocationSchema
from starknet_py.net.schemas.rpc.execution_resources import ExecutionResourcesSchema
from starknet_py.net.schemas.rpc.function_invocation import FunctionInvocationSchema
from starknet_py.net.schemas.rpc.state_diff import StateDiffSchema
from starknet_py.utils.schema import Schema


class InvokeTransactionTraceSchema(Schema):
    execute_invocation = fields.Nested(
        ExecuteInvocationSchema(), data_key="execute_invocation", required=True
    )
    execution_resources = fields.Nested(
        ExecutionResourcesSchema(), data_key="execution_resources", required=True
    )
    validate_invocation = fields.Nested(
        FunctionInvocationSchema(), data_key="validate_invocation", load_default=None
    )
    fee_transfer_invocation = fields.Nested(
        FunctionInvocationSchema(),
        data_key="fee_transfer_invocation",
        load_default=None,
    )
    state_diff = fields.Nested(
        StateDiffSchema(), data_key="state_diff", load_default=None
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> InvokeTransactionTrace:
        return InvokeTransactionTrace(**data)
