import json
from typing import Tuple, List

from marshmallow import Schema, fields, post_load, pre_load, EXCLUDE
from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.client_models import (
    ContractCode,
    StarknetBlock,
    L1toL2Message,
    L2toL1Message,
    BlockStateUpdate,
    StorageDiff,
    ContractDiff,
    Event,
    EntryPoint,
    EntryPointsByType,
    DeclaredContract,
    InvokeTransaction,
    DeclareTransaction,
    DeployTransaction,
    TransactionReceipt,
)
from starknet_py.net.common_schemas.common_schemas import (
    Felt,
    BlockStatusField,
    StatusField,
    NonPrefixedHex,
)

# pylint: disable=unused-argument
# pylint: disable=no-self-use


class FunctionCallSchema(Schema):
    contract_address = fields.Integer(data_key="contract_address")
    entry_point_selector = fields.Integer(data_key="entry_point_selector")
    calldata = fields.List(fields.Integer(), data_key="calldata")


class EventSchema(Schema):
    from_address = Felt(data_key="from_address")
    keys = fields.List(Felt(), data_key="keys")
    data = fields.List(Felt(), data_key="data")

    @post_load
    def make_dataclass(self, data, **kwargs) -> Event:
        return Event(**data)


class L1toL2MessageSchema(Schema):
    l1_address = Felt(data_key="from_address")
    l2_address = Felt(load_default=None)
    payload = fields.List(Felt(), data_key="payload")

    @post_load
    def make_dataclass(self, data, **kwargs) -> L1toL2Message:
        return L1toL2Message(**data)


class L2toL1MessageSchema(Schema):
    l2_address = Felt(load_default=None)
    l1_address = Felt(data_key="to_address")
    payload = fields.List(Felt(), data_key="payload")

    @post_load
    def make_dataclass(self, data, **kwargs) -> L2toL1Message:
        return L2toL1Message(**data)


class TransactionReceiptSchema(Schema):
    hash = Felt(data_key="txn_hash")
    status = StatusField(data_key="status")
    actual_fee = Felt(data_key="actual_fee")
    rejection_reason = fields.String(data_key="statusData", load_default=None)
    events = fields.List(
        fields.Nested(EventSchema()), data_key="events", load_default=[]
    )
    l1_to_l2_consumed_message = fields.Nested(
        L1toL2MessageSchema(), data_key="l1_origin_message", load_default=None
    )
    l2_to_l1_messages = fields.List(
        fields.Nested(L2toL1MessageSchema()), data_key="messages_sent", load_default=[]
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionReceipt:
        return TransactionReceipt(**data)


class ContractCodeSchema(Schema):
    bytecode = fields.List(Felt(), data_key="bytecode")
    abi = fields.String(data_key="abi")

    @post_load
    def make_dataclass(self, data, **kwargs) -> ContractCode:
        data["abi"] = ContractCodeSchema._abi_to_dict(data["abi"])
        return ContractCode(**data)

    @staticmethod
    def _abi_to_dict(abi: str) -> dict:
        return json.loads(abi)


class TransactionSchema(Schema):
    hash = Felt(data_key="txn_hash")
    signature = fields.List(Felt(), data_key="signature", load_default=[])
    max_fee = Felt(data_key="max_fee", load_default=0)


class InvokeTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address")
    entry_point_selector = Felt(data_key="entry_point_selector")
    calldata = fields.List(Felt(), data_key="calldata")

    @pre_load
    def preprocess(self, data, **kwargs):
        if data["calldata"] is None:
            data["calldata"] = []
        return data

    @post_load
    def make_transaction(self, data, **kwargs) -> InvokeTransaction:
        return InvokeTransaction(**data)


class DeclareTransactionSchema(TransactionSchema):
    class_hash = Felt(data_key="class_hash")
    sender_address = Felt(data_key="sender_address")

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransaction:
        return DeclareTransaction(**data)


class DeployTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address")
    constructor_calldata = fields.List(Felt(), data_key="calldata")
    # class_hash = Felt(data_key="class_hash", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployTransaction:
        return DeployTransaction(**data)


class TypesOfTransactionsSchema(OneOfSchema):
    type_field = "type"
    type_schemas = {
        "INVOKE_FUNCTION": InvokeTransactionSchema,
        "DECLARE": DeclareTransactionSchema,
        "DEPLOY": DeployTransactionSchema,
    }

    def get_data_type(self, data):
        if "contract_class" in data:
            return "DECLARE"
        if "entry_point_selector" in data and data["entry_point_selector"] is not None:
            return "INVOKE_FUNCTION"
        return "DEPLOY"


class StarknetBlockSchema(Schema):
    block_hash = Felt(data_key="block_hash")
    parent_block_hash = Felt(data_key="parent_hash")
    block_number = fields.Integer(data_key="block_number")
    status = BlockStatusField(data_key="status")
    root = NonPrefixedHex(data_key="new_root")
    transactions = fields.List(
        fields.Nested(TypesOfTransactionsSchema(unknown=EXCLUDE)),
        data_key="transactions",
    )
    timestamp = fields.Integer(data_key="timestamp")

    @post_load
    def make_dataclass(self, data, **kwargs) -> StarknetBlock:
        return StarknetBlock(**data)


class StorageDiffSchema(Schema):
    address = Felt(data_key="address")
    key = Felt(data_key="key")
    value = Felt(data_key="value")

    @post_load
    def make_dataclass(self, data, **kwargs) -> StorageDiff:
        return StorageDiff(**data)


class ContractDiffSchema(Schema):
    address = Felt(data_key="address")
    contract_hash = Felt(data_key="contract_hash")

    @post_load
    def make_dataclass(self, data, **kwargs) -> ContractDiff:
        return ContractDiff(**data)


class StateDiffSchema(Schema):
    storage_diffs = fields.List(
        fields.Nested(StorageDiffSchema()), data_key="storage_diffs"
    )
    contract_diffs = fields.List(
        fields.Nested(ContractDiffSchema()), data_key="contracts"
    )


class BlockStateUpdateSchema(Schema):
    block_hash = Felt(data_key="block_hash")
    new_root = Felt(data_key="new_root")
    old_root = Felt(data_key="old_root")
    state_diff = fields.Nested(StateDiffSchema(), data_key="state_diff")

    @pre_load
    def preprocess(self, data, **kwargs):
        # Remove this when support for nonces is added
        del data["state_diff"]["nonces"]

        return data

    @post_load
    def make_dataclass(self, data, **kwargs) -> BlockStateUpdate:
        storage_diffs, contract_diffs = BlockStateUpdateSchema._extract_diffs(
            data["state_diff"]
        )
        del data["state_diff"]

        return BlockStateUpdate(
            **data, storage_diffs=storage_diffs, contract_diffs=contract_diffs
        )

    @staticmethod
    def _extract_diffs(
        state_diff: dict,
    ) -> Tuple[List[StorageDiff], List[ContractDiff]]:
        storage_diffs = state_diff["storage_diffs"]
        contract_diffs = state_diff["contract_diffs"]
        return storage_diffs, contract_diffs


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


class DeclaredContractSchema(Schema):
    program = fields.String(data_key="program")
    entry_points_by_type = fields.Nested(
        EntryPointsByTypeSchema(), data_key="entry_points_by_type"
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclaredContract:
        return DeclaredContract(**data)
