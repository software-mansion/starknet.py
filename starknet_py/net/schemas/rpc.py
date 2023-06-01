from marshmallow import EXCLUDE, Schema, fields, post_load
from marshmallow_oneofschema import OneOfSchema

from starknet_py.abi.schemas import ContractAbiEntrySchema
from starknet_py.net.client_models import (
    BlockStateUpdate,
    ContractClass,
    ContractsNonce,
    DeclaredContractHash,
    DeclareTransaction,
    DeclareTransactionResponse,
    DeployAccountTransaction,
    DeployAccountTransactionResponse,
    DeployedContract,
    DeployTransaction,
    EntryPoint,
    EntryPointsByType,
    EstimatedFee,
    Event,
    EventsChunk,
    InvokeTransaction,
    L1HandlerTransaction,
    L1toL2Message,
    L2toL1Message,
    PendingBlockStateUpdate,
    ReplacedClass,
    SentTransactionResponse,
    SierraContractClass,
    SierraEntryPoint,
    SierraEntryPointsByType,
    StarknetBlock,
    StateDiff,
    StorageDiffItem,
    TransactionReceipt,
)
from starknet_py.net.schemas.common import (
    BlockStatusField,
    Felt,
    NonPrefixedHex,
    StatusField,
    StorageEntrySchema,
)
from starknet_py.net.schemas.utils import (
    _replace_invoke_contract_address_with_sender_address,
)

# pylint: disable=unused-argument, no-self-use


class FunctionCallSchema(Schema):
    contract_address = fields.Integer(data_key="contract_address", required=True)
    entry_point_selector = fields.Integer(
        data_key="entry_point_selector", required=True
    )
    calldata = fields.List(fields.Integer(), data_key="calldata", required=True)


class EventSchema(Schema):
    from_address = Felt(data_key="from_address", required=True)
    keys = fields.List(Felt(), data_key="keys", required=True)
    data = fields.List(Felt(), data_key="data", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Event:
        return Event(**data)


class EventsChunkSchema(Schema):
    events = fields.List(
        fields.Nested(EventSchema(unknown=EXCLUDE)),
        data_key="events",
        required=True,
    )
    continuation_token = fields.String(data_key="continuation_token", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return EventsChunk(**data)


class L1toL2MessageSchema(Schema):
    l1_address = Felt(data_key="from_address", required=True)
    l2_address = Felt(load_default=None)
    payload = fields.List(Felt(), data_key="payload", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> L1toL2Message:
        return L1toL2Message(**data)


class L2toL1MessageSchema(Schema):
    l2_address = Felt(load_default=None)
    l1_address = Felt(data_key="to_address", required=True)
    payload = fields.List(Felt(), data_key="payload", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> L2toL1Message:
        return L2toL1Message(**data)


class TransactionReceiptSchema(Schema):
    hash = Felt(data_key="transaction_hash", required=True)
    status = StatusField(data_key="status", required=True)
    block_number = fields.Integer(data_key="block_number", load_default=None)
    block_hash = Felt(data_key="block_hash", load_default=None)
    actual_fee = Felt(data_key="actual_fee", required=True)
    rejection_reason = fields.String(data_key="status_data", load_default=None)
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


class EstimatedFeeSchema(Schema):
    overall_fee = Felt(data_key="overall_fee", required=True)
    gas_price = Felt(data_key="gas_price", required=True)
    gas_usage = Felt(data_key="gas_consumed", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return EstimatedFee(**data)


class TransactionSchema(Schema):
    hash = Felt(data_key="transaction_hash", required=True)
    signature = fields.List(Felt(), data_key="signature", load_default=[])
    max_fee = Felt(data_key="max_fee", load_default=0)
    version = Felt(data_key="version", required=True)


class InvokeTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address", load_default=None)
    sender_address = Felt(data_key="sender_address", load_default=None)
    entry_point_selector = Felt(data_key="entry_point_selector", load_default=None)
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    nonce = Felt(data_key="nonce", load_default=None)

    @post_load
    def make_transaction(self, data, **kwargs) -> InvokeTransaction:
        _replace_invoke_contract_address_with_sender_address(data)
        return InvokeTransaction(**data)


class DeclareTransactionSchema(TransactionSchema):
    class_hash = Felt(data_key="class_hash", required=True)
    sender_address = Felt(data_key="sender_address", required=True)
    nonce = Felt(data_key="nonce", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransaction:
        return DeclareTransaction(**data)


class DeployTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address", load_default=None)
    constructor_calldata = fields.List(
        Felt(), data_key="constructor_calldata", required=True
    )
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployTransaction:
        return DeployTransaction(**data)


class DeployAccountTransactionSchema(TransactionSchema):
    contract_address_salt = Felt(data_key="contract_address_salt", required=True)
    constructor_calldata = fields.List(
        Felt(), data_key="constructor_calldata", required=True
    )
    class_hash = Felt(data_key="class_hash", required=True)
    nonce = Felt(data_key="nonce", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployAccountTransaction:
        return DeployAccountTransaction(**data)


class L1HandlerTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address", required=True)
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    entry_point_selector = Felt(data_key="entry_point_selector", required=True)
    nonce = Felt(data_key="nonce", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> L1HandlerTransaction:
        return L1HandlerTransaction(**data)


class TypesOfTransactionsSchema(OneOfSchema):
    type_field = "type"
    type_schemas = {
        "INVOKE": InvokeTransactionSchema,
        "DECLARE": DeclareTransactionSchema,
        "DEPLOY": DeployTransactionSchema,
        "DEPLOY_ACCOUNT": DeployAccountTransactionSchema,
        "L1_HANDLER": L1HandlerTransactionSchema,
    }


class StarknetBlockSchema(Schema):
    block_hash = Felt(data_key="block_hash", required=True)
    parent_block_hash = Felt(data_key="parent_hash", required=True)
    block_number = fields.Integer(data_key="block_number", required=True)
    status = BlockStatusField(data_key="status", required=True)
    root = NonPrefixedHex(data_key="new_root", required=True)
    transactions = fields.List(
        fields.Nested(TypesOfTransactionsSchema(unknown=EXCLUDE)),
        data_key="transactions",
        required=True,
    )
    timestamp = fields.Integer(data_key="timestamp", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> StarknetBlock:
        return StarknetBlock(**data)


class StorageDiffSchema(Schema):
    address = Felt(data_key="address", required=True)
    storage_entries = fields.List(
        fields.Nested(StorageEntrySchema()),
        data_key="storage_entries",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> StorageDiffItem:
        return StorageDiffItem(**data)


class ContractDiffSchema(Schema):
    address = Felt(data_key="address", required=True)
    contract_hash = Felt(data_key="contract_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployedContract:
        return DeployedContract(**data)


class DeclaredContractHashSchema(Schema):
    class_hash = Felt(data_key="class_hash", required=True)
    compiled_class_hash = Felt(data_key="compiled_class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclaredContractHash:
        return DeclaredContractHash(**data)


class DeployedContractSchema(Schema):
    address = Felt(data_key="address", required=True)
    class_hash = NonPrefixedHex(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return DeployedContract(**data)


class ContractsNonceSchema(Schema):
    contract_address = Felt(data_key="contract_address", required=True)
    nonce = Felt(data_key="nonce", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return ContractsNonce(**data)


class ReplacedClassSchema(Schema):
    contract_address = Felt(data_key="contract_address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ReplacedClass:
        return ReplacedClass(**data)


class StateDiffSchema(Schema):
    storage_diffs = fields.List(
        fields.Nested(StorageDiffSchema()),
        data_key="storage_diffs",
        required=True,
    )
    deprecated_declared_classes = fields.List(
        Felt(),
        data_key="deprecated_declared_classes",
        required=True,
    )
    declared_classes = fields.List(
        fields.Nested(DeclaredContractHashSchema()),
        data_key="declared_classes",
        required=True,
    )
    deployed_contracts = fields.List(
        fields.Nested(DeployedContractSchema()),
        data_key="deployed_contracts",
        required=True,
    )
    replaced_classes = fields.List(
        fields.Nested(ReplacedClassSchema()),
        data_key="replaced_classes",
        required=True,
    )
    nonces = fields.List(
        fields.Nested(ContractsNonceSchema()), data_key="nonces", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> StateDiff:
        return StateDiff(**data)


class BlockStateUpdateSchema(Schema):
    block_hash = Felt(data_key="block_hash", required=True)
    new_root = Felt(data_key="new_root", required=True)
    old_root = Felt(data_key="old_root", required=True)
    state_diff = fields.Nested(StateDiffSchema(), data_key="state_diff", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> BlockStateUpdate:
        return BlockStateUpdate(
            **data,
        )


class PendingBlockStateUpdateSchema(Schema):
    old_root = Felt(data_key="old_root", required=True)
    state_diff = fields.Nested(StateDiffSchema(), data_key="state_diff", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> PendingBlockStateUpdate:
        return PendingBlockStateUpdate(**data)


class SierraEntryPointSchema(Schema):
    selector = Felt(data_key="selector", required=True)
    function_idx = fields.Integer(data_key="function_idx", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraEntryPoint:
        return SierraEntryPoint(**data)


class EntryPointSchema(Schema):
    offset = Felt(data_key="offset", required=True)
    selector = Felt(data_key="selector", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EntryPoint:
        return EntryPoint(**data)


class SierraEntryPointsByTypeSchema(Schema):
    constructor = fields.List(
        fields.Nested(SierraEntryPointSchema()), data_key="CONSTRUCTOR", required=True
    )
    external = fields.List(
        fields.Nested(SierraEntryPointSchema()), data_key="EXTERNAL", required=True
    )
    l1_handler = fields.List(
        fields.Nested(SierraEntryPointSchema()), data_key="L1_HANDLER", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraEntryPointsByType:
        return SierraEntryPointsByType(**data)


class EntryPointsByTypeSchema(Schema):
    constructor = fields.List(
        fields.Nested(EntryPointSchema()), data_key="CONSTRUCTOR", required=True
    )
    external = fields.List(
        fields.Nested(EntryPointSchema()), data_key="EXTERNAL", required=True
    )
    l1_handler = fields.List(
        fields.Nested(EntryPointSchema()), data_key="L1_HANDLER", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> EntryPointsByType:
        return EntryPointsByType(**data)


class SierraContractClassSchema(Schema):
    sierra_program = fields.List(Felt(), data_key="sierra_program", required=True)
    contract_class_version = fields.String(
        data_key="contract_class_version", required=True
    )
    entry_points_by_type = fields.Nested(
        SierraEntryPointsByTypeSchema(), data_key="entry_points_by_type", required=True
    )
    abi = fields.String(data_key="abi", required=False)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraContractClass:
        return SierraContractClass(**data)


class ContractClassSchema(Schema):
    program = fields.String(data_key="program", required=True)
    entry_points_by_type = fields.Nested(
        EntryPointsByTypeSchema(), data_key="entry_points_by_type", required=True
    )
    abi = fields.List(
        fields.Nested(ContractAbiEntrySchema(unknown=EXCLUDE)), data_key="abi"
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ContractClass:
        return ContractClass(**data)


class SentTransactionSchema(Schema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return SentTransactionResponse(**data)


class DeclareTransactionResponseSchema(SentTransactionSchema):
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return DeclareTransactionResponse(**data)


class DeployAccountTransactionResponseSchema(SentTransactionSchema):
    address = Felt(data_key="contract_address", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return DeployAccountTransactionResponse(**data)


class PendingTransactionsSchema(Schema):
    pending_transactions = fields.List(
        fields.Nested(TypesOfTransactionsSchema(unknown=EXCLUDE)),
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs):
        return data["pending_transactions"]
