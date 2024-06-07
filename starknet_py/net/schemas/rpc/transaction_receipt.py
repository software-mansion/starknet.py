from marshmallow import fields, post_load

from starknet_py.net.client_models import TransactionReceipt
from starknet_py.net.schemas.common import (
    ExecutionStatusField,
    Felt,
    FinalityStatusField,
    NumberAsHex,
    TransactionTypeField,
)
from starknet_py.net.schemas.rpc.event import EventSchema
from starknet_py.net.schemas.rpc.execution_resources import ExecutionResourcesSchema
from starknet_py.net.schemas.rpc.fee_payment import FeePaymentSchema
from starknet_py.net.schemas.rpc.l2_to_l1_message import L2toL1MessageSchema
from starknet_py.utils.schema import Schema


class TransactionReceiptSchema(Schema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)
    execution_status = ExecutionStatusField(data_key="execution_status", required=True)
    finality_status = FinalityStatusField(data_key="finality_status", required=True)
    block_number = fields.Integer(data_key="block_number", load_default=None)
    block_hash = Felt(data_key="block_hash", load_default=None)
    actual_fee = fields.Nested(FeePaymentSchema(), data_key="actual_fee", required=True)
    type = TransactionTypeField(data_key="type", required=True)
    contract_address = Felt(data_key="contract_address", load_default=None)
    revert_reason = fields.String(data_key="revert_reason", load_default=None)
    events = fields.List(
        fields.Nested(EventSchema()), data_key="events", load_default=[]
    )
    messages_sent = fields.List(
        fields.Nested(L2toL1MessageSchema()), data_key="messages_sent", load_default=[]
    )
    message_hash = NumberAsHex(data_key="message_hash", load_default=None)
    execution_resources = fields.Nested(
        ExecutionResourcesSchema(), data_key="execution_resources", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionReceipt:
        return TransactionReceipt(**data)
