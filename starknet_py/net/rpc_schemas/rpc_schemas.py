import json

from marshmallow import Schema, fields, post_load, ValidationError
from typing import Any, Mapping, Union

from starknet_py.net.client_models import (
    Transaction,
    TransactionStatus,
    ContractCode,
    BlockStatus,
    StarknetBlock,
)


class Felt(fields.Field):
    # TODO test that serialization and deserialization is correct
    """
    Field that serializes int to felt (hex encoded string)
    """

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        if value is None:
            return None
        return str(hex(value))

    def _deserialize(
        self,
        value: Any,
        attr: Union[str, None],
        data: Union[Mapping[str, Any], None],
        **kwargs,
    ):
        try:
            assert type(value) == str and value.startswith("0x")
            return int(value, 16)
        except (ValueError, AssertionError) as error:
            raise ValidationError("Invalid felt") from error


class StatusField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        # TODO should we serialize to string?
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Union[str, None],
        data: Union[Mapping[str, Any], None],
        **kwargs,
    ):
        # TODO maybe simplify
        enum_values = {v.name: k for k, v in enumerate(TransactionStatus)}

        if value not in enum_values:
            raise ValidationError("Invalid TransactionStatus enum key")

        return TransactionStatus(enum_values[value])


class BlockStatusField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        # TODO should we serialize to string?
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Union[str, None],
        data: Union[Mapping[str, Any], None],
        **kwargs,
    ):
        # TODO maybe simplify
        enum_values = {v.name: k for k, v in enumerate(BlockStatus)}

        if value not in enum_values:
            raise ValidationError("Invalid BlockStatus enum key")

        return BlockStatus(enum_values[value])


class FunctionCallSchema(Schema):
    contract_address = fields.Integer(data_key="contract_address")
    entry_point_selector = fields.Integer(data_key="entry_point_selector")
    calldata = fields.List(fields.Integer(), data_key="calldata")


class TransactionSchema(Schema):
    hash = Felt(data_key="txn_hash")
    contract_address = Felt(data_key="contract_address")
    entry_point_selector = Felt(data_key="entry_point_selector")
    calldata = fields.List(Felt(), data_key="calldata")

    @post_load
    def make_transaction(self, data, **kwargs) -> Transaction:
        # TODO handle kwargs
        return Transaction(**data)


class EventSchema(Schema):
    from_address = Felt(data_key="from_address")
    keys = fields.List(Felt(), data_key="keys")
    data = fields.List(Felt(), data_key="data")


class L1toL2MessageSchema(Schema):
    l1_address = Felt(data_key="from_address")
    l2_address = Felt()
    payload = fields.List(Felt(), data_key="payload")


class L2toL1MessageSchema(Schema):
    l2_address = Felt()
    l1_address = Felt(data_key="to_address")
    payload = fields.List(Felt(), data_key="payload")


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


class ContractCodeSchema(Schema):
    bytecode = fields.List(Felt(), data_key="bytecode")
    abi = fields.String(data_key="abi")

    @post_load
    def make_dataclass(self, data, **kwargs) -> ContractCode:
        parsed_json = json.loads(data["abi"])
        data["abi"] = parsed_json[0]
        return ContractCode(**data)


class StarknetBlockSchema(Schema):
    block_hash = Felt(data_key="block_hash")
    parent_block_hash = Felt(data_key="parent_hash")
    block_number = fields.Integer(data_key="block_number")
    status = BlockStatusField(data_key="status")
    root = Felt(data_key="new_root")
    transactions = fields.List(
        fields.Nested(TransactionSchema()), data_key="transactions"
    )
    timestamp = fields.Integer(data_key="accepted_time")

    @post_load
    def make_dataclass(self, data, **kwargs) -> StarknetBlock:
        return StarknetBlock(**data)
