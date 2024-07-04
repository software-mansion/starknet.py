from marshmallow import EXCLUDE, fields, post_load
from marshmallow_oneofschema.one_of_schema import OneOfSchema

from starknet_py.net.client_models import (
    BlockTransactionTrace,
    ComputationResources,
    DataResources,
    DeclareTransactionTrace,
    DeployAccountTransactionTrace,
    EstimatedFee,
    ExecutionResources,
    FunctionInvocation,
    InvokeTransactionTrace,
    L1HandlerTransactionTrace,
    OrderedEvent,
    OrderedMessage,
    RevertedFunctionInvocation,
    SimulatedTransaction,
)
from starknet_py.net.schemas.common import (
    CallTypeField,
    EntryPointTypeField,
    Felt,
    PriceUnitField,
)
from starknet_py.net.schemas.rpc.block import StateDiffSchema
from starknet_py.utils.schema import Schema

# pylint: disable=unused-argument, no-self-use


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


class ComputationResourcesSchema(Schema):
    steps = fields.Integer(data_key="steps", required=True)
    memory_holes = fields.Integer(data_key="memory_holes", load_default=None)
    range_check_builtin_applications = fields.Integer(
        data_key="range_check_builtin_applications", load_default=None
    )
    pedersen_builtin_applications = fields.Integer(
        data_key="pedersen_builtin_applications", load_default=None
    )
    poseidon_builtin_applications = fields.Integer(
        data_key="poseidon_builtin_applications", load_default=None
    )
    ec_op_builtin_applications = fields.Integer(
        data_key="ec_op_builtin_applications", load_default=None
    )
    ecdsa_builtin_applications = fields.Integer(
        data_key="ecdsa_builtin_applications", load_default=None
    )
    bitwise_builtin_applications = fields.Integer(
        data_key="bitwise_builtin_applications", load_default=None
    )
    keccak_builtin_applications = fields.Integer(
        data_key="keccak_builtin_applications", load_default=None
    )
    segment_arena_builtin = fields.Integer(
        data_key="segment_arena_builtin", load_default=None
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ComputationResources:
        return ComputationResources(**data)


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
    computation_resources = fields.Nested(
        ComputationResourcesSchema(), data_key="execution_resources", required=True
    )

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


class DataResourcesSchema(Schema):
    l1_gas = fields.Integer(data_key="l1_gas", required=True)
    l1_data_gas = fields.Integer(data_key="l1_data_gas", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DataResources:
        return DataResources(**data)


class ExecutionResourcesSchema(ComputationResourcesSchema):
    data_availability = fields.Nested(
        DataResourcesSchema(), data_key="data_availability", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ExecutionResources:
        return ExecutionResources(**data)


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


class EstimatedFeeSchema(Schema):
    gas_consumed = Felt(data_key="gas_consumed", required=True)
    gas_price = Felt(data_key="gas_price", required=True)
    data_gas_consumed = Felt(data_key="data_gas_consumed", required=True)
    data_gas_price = Felt(data_key="data_gas_price", required=True)
    overall_fee = Felt(data_key="overall_fee", required=True)
    unit = PriceUnitField(data_key="unit", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EstimatedFee:
        return EstimatedFee(**data)


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
