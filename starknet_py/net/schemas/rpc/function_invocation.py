from marshmallow import fields, post_load

from starknet_py.net.client_models import FunctionInvocation
from starknet_py.net.schemas.common import CallTypeField, EntryPointTypeField, Felt
from starknet_py.net.schemas.rpc.computation_resources import ComputationResourcesSchema
from starknet_py.net.schemas.rpc.ordered_event_schema import OrderedEventSchema
from starknet_py.net.schemas.rpc.ordered_message import OrderedMessageSchema
from starknet_py.utils.schema import Schema


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
