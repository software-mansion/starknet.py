import json
from typing import Any, Dict, List

from marshmallow import EXCLUDE, Schema, fields, post_load
from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.client_models import (
    BlockSingleTransactionTrace,
    BlockStateUpdate,
    BlockTransactionTraces,
    CasmClass,
    CasmClassEntryPoint,
    CasmClassEntryPointsByType,
    CompiledContract,
    ContractClass,
    ContractCode,
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
    GatewayBlock,
    InvokeTransaction,
    L1HandlerTransaction,
    L1toL2Message,
    L2toL1Message,
    ReplacedClass,
    SentTransactionResponse,
    SierraCompiledContract,
    SierraContractClass,
    SierraEntryPoint,
    SierraEntryPointsByType,
    StateDiff,
    StorageDiffItem,
    TransactionReceipt,
    TransactionStatusResponse,
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


class EventSchema(Schema):
    from_address = Felt(data_key="from_address", required=True)
    keys = fields.List(Felt(), data_key="keys", required=True)
    data = fields.List(Felt(), data_key="data", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Event:
        return Event(**data)


class L1toL2MessageSchema(Schema):
    l1_address = Felt(data_key="from_address", required=True)
    l2_address = Felt(data_key="to_address", required=True)
    payload = fields.List(Felt(), data_key="payload", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> L1toL2Message:
        return L1toL2Message(**data)


class L2toL1MessageSchema(Schema):
    l2_address = Felt(data_key="from_address", required=True)
    l1_address = Felt(data_key="to_address", required=True)
    payload = fields.List(Felt(), data_key="payload", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> L2toL1Message:
        return L2toL1Message(**data)


class TransactionSchema(Schema):
    hash = Felt(data_key="transaction_hash", required=True)
    signature = fields.List(Felt(), data_key="signature", load_default=[])
    max_fee = Felt(data_key="max_fee", load_default=0)
    version = Felt(data_key="version", required=True)


class InvokeTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address", load_default=None)
    sender_address = Felt(data_key="sender_address", load_default=None)
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    entry_point_selector = Felt(data_key="entry_point_selector", load_default=None)
    nonce = Felt(data_key="nonce", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> InvokeTransaction:
        _replace_invoke_contract_address_with_sender_address(data)
        return InvokeTransaction(**data)


class DeployTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address", required=True)
    constructor_calldata = fields.List(
        Felt(), data_key="constructor_calldata", required=True
    )
    class_hash = Felt(data_key="class_hash", load_default=0)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployTransaction:
        return DeployTransaction(**data)


class DeclareTransactionSchema(TransactionSchema):
    class_hash = Felt(data_key="class_hash", required=True)
    sender_address = Felt(data_key="sender_address", required=True)
    nonce = Felt(data_key="nonce", load_default=None)
    compiled_class_hash = Felt(data_key="compiled_class_hash", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransaction:
        return DeclareTransaction(**data)


class DeployAccountTransactionSchema(TransactionSchema):
    contract_address_salt = Felt(data_key="contract_address_salt", required=True)
    class_hash = Felt(data_key="class_hash", required=True)
    constructor_calldata = fields.List(
        Felt(), data_key="constructor_calldata", required=True
    )
    nonce = Felt(data_key="nonce", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployAccountTransaction:
        return DeployAccountTransaction(**data)


class L1HandlerTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address", required=True)
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    entry_point_selector = Felt(data_key="entry_point_selector", required=True)
    nonce = Felt(data_key="nonce", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> L1HandlerTransaction:
        return L1HandlerTransaction(**data)


class TypesOfTransactionsSchema(OneOfSchema):
    type_field = "type"
    type_schemas = {
        "INVOKE_FUNCTION": InvokeTransactionSchema,
        "DECLARE": DeclareTransactionSchema,
        "DEPLOY": DeployTransactionSchema,
        "DEPLOY_ACCOUNT": DeployAccountTransactionSchema,
        "L1_HANDLER": L1HandlerTransactionSchema,
    }


class TransactionReceiptSchema(Schema):
    hash = Felt(data_key="transaction_hash", required=True)
    status = StatusField(data_key="status", required=True)
    block_number = fields.Integer(data_key="block_number", load_default=None)
    block_hash = Felt(data_key="block_hash", load_default=None)
    actual_fee = Felt(data_key="actual_fee", allow_none=True)
    rejection_reason = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        data_key="transaction_failure_reason",
        allow_none=True,
        load_default=None,
    )
    events = fields.List(
        fields.Nested(EventSchema()), data_key="events", load_default=[]
    )
    l1_to_l2_consumed_message = fields.Nested(
        L1toL2MessageSchema(), data_key="l1_to_l2_consumed_message", load_default=None
    )
    l2_to_l1_messages = fields.List(
        fields.Nested(L2toL1MessageSchema()),
        data_key="l2_to_l1_messages",
        load_default=[],
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionReceipt:
        if data.get("rejection_reason", None) is not None:
            rejection_reason = data["rejection_reason"]["error_message"]
            del data["rejection_reason"]

            return TransactionReceipt(**data, rejection_reason=rejection_reason)

        return TransactionReceipt(**data)


class ContractCodeSchema(Schema):
    bytecode = fields.List(Felt(), data_key="bytecode", required=True)
    abi = fields.List(
        fields.Dict(keys=fields.String(), values=fields.Raw()),
        data_key="abi",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs):
        return ContractCode(**data)


class StarknetBlockSchema(Schema):
    block_hash = Felt(data_key="block_hash", required=True)
    parent_block_hash = Felt(data_key="parent_block_hash", required=True)
    block_number = fields.Integer(data_key="block_number", required=True)
    status = BlockStatusField(data_key="status", required=True)
    root = NonPrefixedHex(data_key="state_root", required=True)
    transactions = fields.List(
        fields.Nested(TypesOfTransactionsSchema(unknown=EXCLUDE)),
        data_key="transactions",
        required=True,
    )
    timestamp = fields.Integer(data_key="timestamp", required=True)
    gas_price = Felt(data_key="gas_price")

    @post_load
    def make_dataclass(self, data, **kwargs):
        return GatewayBlock(**data)


class BlockSingleTransactionTraceSchema(Schema):
    function_invocation = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        data_key="function_invocation",
        load_default=None,
    )
    validate_invocation = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        data_key="validate_invocation",
        load_default=None,
    )
    fee_transfer_invocation = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        data_key="fee_transfer_invocation",
        load_default=None,
    )
    signature = fields.List(Felt(), data_key="signature", load_default=[])
    transaction_hash = Felt(data_key="transaction_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return BlockSingleTransactionTrace(**data)


class BlockTransactionTracesSchema(Schema):
    traces = fields.List(
        fields.Nested(BlockSingleTransactionTraceSchema(unknown=EXCLUDE)),
        data_key="traces",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs):
        return BlockTransactionTraces(**data)


class EstimatedFeeSchema(Schema):
    overall_fee = fields.Integer(data_key="overall_fee", required=True)
    gas_price = fields.Integer(data_key="gas_price", required=True)
    gas_usage = fields.Integer(data_key="gas_usage", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return EstimatedFee(**data)


class SentTransactionSchema(Schema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)
    code = fields.String(data_key="code", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return SentTransactionResponse(**data)


class DeclareTransactionResponseSchema(SentTransactionSchema):
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return DeclareTransactionResponse(**data)


class DeployAccountTransactionResponseSchema(SentTransactionSchema):
    address = Felt(data_key="address", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return DeployAccountTransactionResponse(**data)


class DeployedContractSchema(Schema):
    address = Felt(data_key="address", required=True)
    class_hash = NonPrefixedHex(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return DeployedContract(**data)


class DeclaredContractHashSchema(Schema):
    class_hash = Felt(data_key="class_hash", required=True)
    compiled_class_hash = Felt(data_key="compiled_class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclaredContractHash:
        return DeclaredContractHash(**data)


class ReplacedClassSchema(Schema):
    contract_address = Felt(data_key="address", required=True)
    class_hash = Felt(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ReplacedClass:
        return ReplacedClass(**data)


class StateDiffSchema(Schema):
    deployed_contracts = fields.List(
        fields.Nested(DeployedContractSchema()),
        data_key="deployed_contracts",
        required=True,
    )
    deprecated_declared_contract_hashes = fields.List(
        Felt(),
        data_key="old_declared_contracts",
        required=True,
    )
    declared_contract_hashes = fields.List(
        fields.Nested(DeclaredContractHashSchema()),
        data_key="declared_classes",
        required=True,
    )
    storage_diffs = fields.Dict(
        keys=fields.String(),
        values=fields.List(fields.Nested(StorageEntrySchema())),
        data_key="storage_diffs",
        required=True,
    )
    nonces = fields.Dict(keys=Felt(), values=Felt(), data_key="nonces", required=True)
    replaced_classes = fields.List(
        fields.Nested(ReplacedClassSchema()), data_key="replaced_classes", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> StateDiff:
        return StateDiff(**data)


class BlockStateUpdateSchema(Schema):
    block_hash = Felt(data_key="block_hash", required=True)
    new_root = NonPrefixedHex(data_key="new_root", required=True)
    old_root = NonPrefixedHex(data_key="old_root", required=True)
    state_diff = fields.Nested(StateDiffSchema(), data_key="state_diff", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        def fix_field(field: Dict, inner_class: Any) -> List[Any]:
            return [inner_class(key, value) for key, value in field.items()]

        fixed_storage_diffs = fix_field(
            data["state_diff"].storage_diffs, StorageDiffItem
        )
        fixed_nonces = fix_field(data["state_diff"].nonces, ContractsNonce)

        data["state_diff"].storage_diffs = fixed_storage_diffs
        data["state_diff"].nonces = fixed_nonces
        return BlockStateUpdate(**data)


class EntryPointSchema(Schema):
    offset = Felt(data_key="offset", required=True)
    selector = Felt(data_key="selector", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EntryPoint:
        return EntryPoint(**data)


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


class ContractClassSchema(Schema):
    program = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(allow_none=True),
        data_key="program",
        required=True,
    )
    entry_points_by_type = fields.Nested(
        EntryPointsByTypeSchema(), data_key="entry_points_by_type", required=True
    )
    abi = fields.List(fields.Dict(), data_key="abi")

    @post_load
    def make_dataclass(self, data, **kwargs) -> ContractClass:
        return ContractClass(**data)


class SierraEntryPointSchema(Schema):
    function_idx = fields.Integer(data_key="function_idx", required=True)
    selector = Felt(data_key="selector", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraEntryPoint:
        return SierraEntryPoint(**data)


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


class SierraContractClassSchema(Schema):
    contract_class_version = fields.String(
        data_key="contract_class_version", required=True
    )
    sierra_program = fields.List(
        fields.String(),
        data_key="sierra_program",
        required=True,
    )
    entry_points_by_type = fields.Nested(
        SierraEntryPointsByTypeSchema(), data_key="entry_points_by_type", required=True
    )
    abi = fields.String(data_key="abi")

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraContractClass:
        return SierraContractClass(**data)


class SierraCompiledContractSchema(SierraContractClassSchema):
    abi = fields.List(fields.Dict(), data_key="abi", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraCompiledContract:
        # Schema must accept ABI as List[dict] to be compatible with the output of Cairo1 compiler.
        data["abi"] = json.dumps(data["abi"])

        return SierraCompiledContract(**data)


class TypesOfContractClassSchema(OneOfSchema):
    type_schemas = {
        "program": ContractClassSchema(),
        "sierra_program": SierraContractClassSchema(),
    }

    def get_data_type(self, data):
        if "sierra_program" in data:
            return "sierra_program"

        return "program"


class CompiledContractSchema(ContractClassSchema):
    abi = fields.List(fields.Dict(), data_key="abi", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> CompiledContract:
        return CompiledContract(**data)


class CasmClassEntryPointSchema(Schema):
    selector = Felt(data_key="selector", required=True)
    offset = fields.Integer(data_key="offset", required=True)
    builtins = fields.List(fields.String(), data_key="builtins")

    @post_load
    def make_dataclass(self, data, **kwargs) -> CasmClassEntryPoint:
        return CasmClassEntryPoint(**data)


class CasmClassEntryPointsByTypeSchema(Schema):
    constructor = fields.List(
        fields.Nested(CasmClassEntryPointSchema()),
        data_key="CONSTRUCTOR",
        required=True,
    )
    external = fields.List(
        fields.Nested(CasmClassEntryPointSchema()),
        data_key="EXTERNAL",
        required=True,
    )
    l1_handler = fields.List(
        fields.Nested(CasmClassEntryPointSchema()),
        data_key="L1_HANDLER",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> CasmClassEntryPointsByType:
        return CasmClassEntryPointsByType(**data)


class CasmClassSchema(Schema):
    prime = Felt(data_key="prime", required=True)
    bytecode = fields.List(Felt(), data_key="bytecode", required=True)
    hints = fields.List(fields.Raw(), data_key="hints", required=True)
    pythonic_hints = fields.List(fields.Raw(), data_key="pythonic_hints", required=True)
    compiler_version = fields.String(data_key="compiler_version", required=True)
    entry_points_by_type = fields.Nested(
        CasmClassEntryPointsByTypeSchema(),
        data_key="entry_points_by_type",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> CasmClass:
        return CasmClass(**data)


class TransactionStatusSchema(Schema):
    transaction_status = StatusField(data_key="tx_status", required=True)
    block_hash = Felt(data_key="block_hash", allow_none=True)

    @post_load
    def make_result(self, data, **kwargs) -> TransactionStatusResponse:
        return TransactionStatusResponse(**data)
