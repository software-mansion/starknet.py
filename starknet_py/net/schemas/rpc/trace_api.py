from marshmallow import EXCLUDE, fields, post_load
from marshmallow_oneofschema.one_of_schema import OneOfSchema

from starknet_py.net.client_models import (
    BlockTransactionTrace,
    DeclareTransactionTrace,
    DeployAccountTransactionTrace,
    FunctionInvocation,
    InvokeTransactionTrace,
    L1HandlerTransactionTrace,
    OrderedEvent,
    OrderedMessage,
    RevertedFunctionInvocation,
    SimulatedTransaction,
)
from starknet_py.net.schemas.common import CallTypeField, EntryPointTypeField, Felt
from starknet_py.net.schemas.rpc.block import StateDiffSchema
from starknet_py.net.schemas.rpc.general import (
    EstimatedFeeSchema,
    ExecutionResourcesSchema,
    InnerCallExecutionResourcesSchema,
)
from starknet_py.utils.schema import Schema


class OrderedEventSchema(Schema):
    keys = fields.List(Felt(), data_key="keys", required=True)
    data = fields.List(Felt(), data_key="data", required=True)
    order = fields.Integer(data_key="order", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return OrderedEvent(**data)


class OrderedMessageSchema(Schema):
    l2_address = Felt(data_key="from_address", required=True)
    l1_address = Felt(data_key="to_address", required=True)
    payload = fields.List(Felt(), data_key="payload", required=True)
    order = fields.Integer(data_key="order", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> OrderedMessage:
        return OrderedMessage(**data)


class FunctionInvocationSchema(Schema):
    contract_address = Felt(data_key="contract_address", required=True)
    entry_point_selector = Felt(data_key="entry_point_selector", required=True)
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    caller_address = Felt(data_key="caller_address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)
    entry_point_type = EntryPointTypeField(data_key="entry_point_type", required=True)
    call_type = CallTypeField(data_key="call_type", required=True)
    result = fields.List(Felt(), data_key="result", required=True)
    # https://marshmallow.readthedocs.io/en/stable/nesting.html#nesting-a-schema-within-itself
    calls = fields.List(
        fields.Nested(
            lambda: FunctionInvocationSchema()  # pylint: disable=unnecessary-lambda
        ),
        data_key="calls",
        required=True,
    )
    events = fields.List(
        fields.Nested(OrderedEventSchema()), data_key="events", required=True
    )
    messages = fields.List(
        fields.Nested(OrderedMessageSchema()), data_key="messages", required=True
    )
    execution_resources = fields.Nested(
        InnerCallExecutionResourcesSchema(),
        data_key="execution_resources",
        required=True,
    )
    is_reverted = fields.Boolean(data_key="is_reverted", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> FunctionInvocation:
        return FunctionInvocation(**data)


class RevertedFunctionInvocationSchema(Schema):
    revert_reason = fields.String(data_key="revert_reason", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> RevertedFunctionInvocation:
        return RevertedFunctionInvocation(**data)


class ExecuteInvocationSchema(OneOfSchema):
    type_schemas = {
        "REVERTED": RevertedFunctionInvocationSchema(),
        "FUNCTION_INVOCATION": FunctionInvocationSchema(),
    }

    def get_data_type(self, data):
        if "revert_reason" in data:
            return "REVERTED"
        return "FUNCTION_INVOCATION"


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


class DeclareTransactionTraceSchema(Schema):
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
    def make_dataclass(self, data, **kwargs) -> DeclareTransactionTrace:
        return DeclareTransactionTrace(**data)


class DeployAccountTransactionTraceSchema(Schema):
    constructor_invocation = fields.Nested(
        FunctionInvocationSchema(), data_key="constructor_invocation", required=True
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
    def make_dataclass(self, data, **kwargs) -> DeployAccountTransactionTrace:
        return DeployAccountTransactionTrace(**data)


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


class TransactionTraceSchema(OneOfSchema):
    type_field = "type"

    type_schemas = {
        "INVOKE": InvokeTransactionTraceSchema(),
        "DECLARE": DeclareTransactionTraceSchema(),
        "DEPLOY_ACCOUNT": DeployAccountTransactionTraceSchema(),
        "L1_HANDLER": L1HandlerTransactionTraceSchema(),
    }


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


class BlockTransactionTraceSchema(Schema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)
    # `unknown=EXCLUDE` in order to skip `type=...` field we don't want
    trace_root = fields.Nested(
        TransactionTraceSchema(), data_key="trace_root", required=True, unknown=EXCLUDE
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> BlockTransactionTrace:
        return BlockTransactionTrace(**data)
