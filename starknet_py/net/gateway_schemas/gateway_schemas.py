from marshmallow import Schema, fields, post_load, pre_load, EXCLUDE

from starknet_py.net.client_models import (
    Transaction,
    ContractCode,
    StarknetBlock,
    TransactionReceipt,
    L2toL1Message,
    L1toL2Message,
    SentTransaction,
    ContractDiff,
    StorageDiff,
    BlockStateUpdate,
    EntryPoint,
    EntryPointsByType,
    ContractClass,
)
from starknet_py.net.common_schemas.common_schemas import (
    Felt,
    BlockStatusField,
    StatusField,
    TransactionTypeField,
    NonPrefixedHex,
)

# pylint: disable=unused-argument
# pylint: disable=no-self-use


class EventSchema(Schema):
    from_address = Felt(data_key="from_address")
    keys = fields.List(Felt(), data_key="keys")
    data = fields.List(Felt(), data_key="data")


class L1toL2MessageSchema(Schema):
    # TODO handle missing fields
    l1_address = Felt(data_key="from_address")
    l2_address = Felt(data_key="to_address")
    payload = fields.List(Felt(), data_key="payload")

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
    entry_point_selector = Felt(data_key="entry_point_selector", load_default=0)
    calldata = fields.List(Felt(), data_key="calldata")
    transaction_type = TransactionTypeField(data_key="type")
    # TODO verify this field actually exists
    version = fields.Integer(data_key="version", load_default=0)
    max_fee = Felt(data_key="max_fee", load_default=0)

    @pre_load
    def preprocess(self, data, **kwargs):
        if "constructor_calldata" in data:
            data["calldata"] = data["constructor_calldata"]
            del data["constructor_calldata"]
        return data

    @post_load
    def make_dataclass(self, data, **kwargs) -> Transaction:
        return Transaction(**data)


class TransactionReceiptSchema(Schema):
    hash = Felt(data_key="transaction_hash")
    status = StatusField(data_key="status")
    events = fields.List(fields.Nested(EventSchema()), data_key="events")
    l1_to_l2_consumed_message = fields.Nested(
        L1toL2MessageSchema(), data_key="l1_to_l2_consumed_message", allow_none=True
    )
    l2_to_l1_messages = fields.List(
        fields.Nested(L2toL1MessageSchema()), data_key="l2_to_l1_messages"
    )
    block_number = fields.Integer(data_key="block_number", load_default=None)
    version = fields.Integer(data_key="version", allow_none=True)
    actual_fee = Felt(data_key="actual_key", allow_none=True)
    transaction_rejection_reason = fields.String(
        data_key="transaction_rejection_reason", allow_none=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionReceipt:
        return TransactionReceipt(**data)


class ContractCodeSchema(Schema):
    bytecode = fields.List(Felt(), data_key="bytecode")
    # TODO check if using raw is correct
    abi = fields.List(
        fields.Dict(keys=fields.String(), values=fields.Raw()), data_key="abi"
    )

    @post_load
    def make_dataclass(self, data, **kwargs):
        return ContractCode(**data)


class StarknetBlockSchema(Schema):
    block_hash = Felt(data_key="block_hash")
    parent_block_hash = Felt(data_key="parent_block_hash")
    block_number = fields.Integer(data_key="block_number")
    status = BlockStatusField(data_key="status")
    root = NonPrefixedHex(data_key="state_root")
    transactions = fields.List(
        fields.Nested(TransactionSchema(), unknown=EXCLUDE), data_key="transactions"
    )
    timestamp = fields.Integer(data_key="timestamp")

    @post_load
    def make_dataclass(self, data, **kwargs):
        return StarknetBlock(**data)


class SentTransactionSchema(Schema):
    # TODO verify data_keys
    hash = Felt(data_key="transaction_hash")
    code = fields.String(data_key="code")
    address = Felt(data_key="address", allow_none=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return SentTransaction(**data)


class StorageDiffSchema(Schema):
    address = Felt(data_key="address")
    key = Felt(data_key="key")
    value = Felt(data_key="value")

    @post_load
    def make_dataclass(self, data, **kwargs):
        return StorageDiff(**data)


class ContractDiffsSchema(Schema):
    address = Felt(data_key="address")
    contract_hash = NonPrefixedHex(data_key="class_hash")

    @post_load
    def make_dataclass(self, data, **kwargs):
        return ContractDiff(**data)


class BlockStateUpdateSchema(Schema):
    block_hash = Felt(data_key="block_hash")
    new_root = NonPrefixedHex(data_key="new_root")
    old_root = NonPrefixedHex(data_key="old_root")
    state_diff = fields.Dict(
        keys=fields.String(), values=fields.Raw(), data_key="state_diff"
    )

    @post_load
    def make_dataclass(self, data, **kwargs):
        contracts_diffs = data["state_diff"]["deployed_contracts"]
        contracts_diffs = [
            ContractDiffsSchema().load(contract) for contract in contracts_diffs
        ]

        storage_diffs = []
        for address, diffs in data["state_diff"]["storage_diffs"].items():
            for diff in diffs:
                storage_diff = StorageDiffSchema().load(
                    {"address": address, "key": diff["key"], "value": diff["value"]}
                )
                storage_diffs.append(storage_diff)

        del data["state_diff"]

        return BlockStateUpdate(
            **data, storage_diffs=storage_diffs, contract_diffs=contracts_diffs
        )


class EntryPointSchema(Schema):
    offset = Felt(data_key="offset")
    selector = Felt(data_key="selector")

    @post_load
    def make_dataclass(self, data, **kwargs) -> EntryPoint:
        return EntryPoint(**data)


class EntryPointsByTypeSchema(Schema):
    constructor = fields.List(fields.Nested(EntryPointSchema()), data_key="CONSTRUCTOR")
    external = fields.List(fields.Nested(EntryPointSchema()), data_key="EXTERNAL")
    l1_handler = fields.List(fields.Nested(EntryPointSchema()), data_key="L1_HANDLER")

    @post_load
    def make_dataclass(self, data, **kwargs) -> EntryPointsByType:
        return EntryPointsByType(**data)


class ContractClassSchema(Schema):
    # TODO check if using raw is correct
    program = fields.Dict(keys=fields.String(), values=fields.Raw(), data_key="program")
    entry_points_by_type = fields.Nested(
        EntryPointsByTypeSchema(), data_key="entry_points_by_type"
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ContractClass:
        return ContractClass(**data)
