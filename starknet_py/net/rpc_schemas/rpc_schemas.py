import json
from marshmallow import Schema, fields, post_load

from starknet_py.net.client_models import (
    Transaction,
    ContractCode,
    StarknetBlock,
    TransactionType,
    TransactionReceipt,
    L1toL2Message,
    L2toL1Message,
)
from starknet_py.net.common_schemas.common_schemas import (
    Felt,
    BlockStatusField,
    StatusField,
)

# pylint: disable=no-self-use


class FunctionCallSchema(Schema):
    contract_address = fields.Integer(data_key="contract_address")
    entry_point_selector = fields.Integer(data_key="entry_point_selector")
    calldata = fields.List(fields.Integer(), data_key="calldata")


class TransactionSchema(Schema):
    hash = Felt(data_key="txn_hash")
    contract_address = Felt(data_key="contract_address")
    entry_point_selector = Felt(data_key="entry_point_selector", allow_none=True)
    calldata = fields.List(Felt(), data_key="calldata", allow_none=True)

    @post_load
    def make_transaction(self, data, **kwargs) -> Transaction:
        # pylint: disable=unused-argument
        if data["calldata"] is None:
            data["calldata"] = []

        if data["entry_point_selector"] is None:
            data["entry_point_selector"] = 0
            data["transaction_type"] = TransactionType.DEPLOY

        return Transaction(**data)


class EventSchema(Schema):
    from_address = Felt(data_key="from_address")
    keys = fields.List(Felt(), data_key="keys")
    data = fields.List(Felt(), data_key="data")


class L1toL2MessageSchema(Schema):
    # TODO handle missing fields
    l1_address = Felt(data_key="from_address")
    l2_address = Felt(load_default=0x0)
    payload = fields.List(Felt(), data_key="payload")

    @post_load
    def make_dataclass(self, data, **kwargs) -> L1toL2Message:
        # pylint: disable=unused-argument
        return L1toL2Message(**data)


class L2toL1MessageSchema(Schema):
    # TODO handle missing fields
    l2_address = Felt(load_default=0x0)
    l1_address = Felt(data_key="to_address")
    payload = fields.List(Felt(), data_key="payload")

    @post_load
    def make_dataclass(self, data, **kwargs) -> L2toL1Message:
        # pylint: disable=unused-argument
        return L2toL1Message(**data)


class TransactionReceiptSchema(Schema):
    hash = Felt(data_key="txn_hash")
    status = StatusField(data_key="status")
    events = fields.List(fields.Nested(EventSchema()), data_key="events")
    l1_to_l2_consumed_message = fields.Nested(
        L1toL2MessageSchema(), data_key="l1_origin_message", allow_none=True
    )
    l2_to_l1_messages = fields.List(
        fields.Nested(L2toL1MessageSchema()), data_key="messages_sent"
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionReceipt:
        # pylint: disable=unused-argument
        return TransactionReceipt(**data)


class ContractCodeSchema(Schema):
    bytecode = fields.List(Felt(), data_key="bytecode")
    abi = fields.String(data_key="abi")

    @post_load
    def make_dataclass(self, data, **kwargs) -> ContractCode:
        # pylint: disable=unused-argument
        parsed_json = json.loads(data["abi"])
        data["abi"] = parsed_json
        return ContractCode(**data)


class StarknetBlockSchema(Schema):
    block_hash = Felt(data_key="block_hash")
    parent_block_hash = Felt(data_key="parent_hash")
    block_number = fields.Integer(data_key="block_number")
    status = BlockStatusField(data_key="status")
    root = fields.String(data_key="new_root")
    transactions = fields.List(
        fields.Nested(TransactionSchema()), data_key="transactions"
    )
    timestamp = fields.Integer(data_key="accepted_time")

    @post_load
    def make_dataclass(self, data, **kwargs) -> StarknetBlock:
        # pylint: disable=unused-argument
        data["root"] = int(data["root"], 16)

        return StarknetBlock(**data)
