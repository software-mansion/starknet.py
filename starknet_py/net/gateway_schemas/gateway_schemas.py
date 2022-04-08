from typing import List

from marshmallow import Schema, fields, post_load, EXCLUDE

from starknet_py.net.client_models import (
    Transaction,
    ContractCode,
    StarknetBlock,
    TransactionReceipt,
    L2toL1Message,
    L1toL2Message,
)
from starknet_py.net.common_schemas.common_schemas import (
    Felt,
    BlockStatusField,
    StatusField,
)


class EventSchema(Schema):
    from_address = Felt(data_key="from_address")
    keys = fields.List(Felt(), data_key="keys")
    data = fields.List(Felt(), data_key="data")


class L1toL2MessageSchema(Schema):
    # TODO handle missing fields
    l1_address = Felt()
    l2_address = Felt()
    payload = fields.List(Felt())

    @post_load
    def make_dataclass(self, data, **kwargs) -> L1toL2Message:
        return L1toL2Message(**data)


class L2toL1MessageSchema(Schema):
    l2_address = Felt(data_key="from_address")
    l1_address = Felt(data_key="to_address")
    payload = fields.List(Felt(), data_key="payload")

    @post_load
    def make_dataclass(self, data, **kwargs) -> L2toL1Message:
        return L2toL1Message(**data)


class TransactionSchema(Schema):
    hash = Felt(data_key="transaction_hash")
    contract_address = Felt(data_key="contract_address")
    entry_point_selector = Felt(data_key="entry_point_selector")
    calldata = fields.List(Felt(), data_key="calldata")

    @post_load
    def make_dataclass(self, data, **kwargs) -> Transaction:
        # TODO handle kwargs
        return Transaction(**data)


class TransactionReceiptSchema(Schema):
    hash = Felt(data_key="transaction_hash")
    status = StatusField()
    events: fields.List(fields.Nested(EventSchema()))
    l1_to_l2_consumed_message = fields.Nested(L1toL2MessageSchema())
    l2_to_l1_messages = fields.List(fields.Nested(L2toL1MessageSchema()))

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionReceipt:
        return TransactionReceipt(**data)


class ContractCodeSchema(Schema):
    bytecode = fields.List(Felt(), data_key="bytecode")
    abi = fields.List(
        fields.Dict(keys=fields.String(), values=fields.Raw()), data_key="abi"
    )

    @post_load
    def make_dataclass(self, data, **kwargs):
        return ContractCode(bytecode=data["bytecode"], abi=data["abi"][0])


class InvokeSpecificInfoSchema(Schema):
    transaction = fields.Nested(TransactionSchema())


class StarknetBlockSchema(Schema):
    block_hash = Felt(data_key="block_hash")
    parent_block_hash = Felt(data_key="parent_block_hash")
    block_number = fields.Integer(data_key="block_number")
    status = BlockStatusField(data_key="status")
    root = fields.String(data_key="state_root")
    transactions = fields.List(
        fields.Nested(TransactionSchema(), unknown=EXCLUDE), data_key="transactions"
    )
    timestamp = fields.Integer(data_key="timestamp")

    @post_load
    def make_dataclass(self, data, **kwargs):
        data["root"] = int(data["root"], 16)
        return StarknetBlock(**data)


class FunctionCallSchema(Schema):
    # TODO add data_keys
    contract_address = Felt()
    entry_point_selector = Felt()
    calldata = fields.List(Felt())
    signature = fields.List(Felt())
    max_fee = Felt()
    version = Felt()
