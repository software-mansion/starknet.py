from typing import cast

from marshmallow import Schema, fields, post_load, EXCLUDE
from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.client_models import (
    ContractCode,
    GatewayBlock,
    L2toL1Message,
    L1toL2Message,
    SentTransactionResponse,
    DeployedContract,
    StorageDiff,
    BlockStateUpdate,
    EntryPoint,
    EntryPointsByType,
    DeclaredContract,
    InvokeTransaction,
    DeployTransaction,
    DeclareTransaction,
    TransactionReceipt,
    TransactionStatusResponse,
    BlockTransactionTraces,
    BlockSingleTransactionTrace,
    EstimatedFee,
    Event,
    DeclareTransactionResponse,
    DeployTransactionResponse,
    DeployAccountTransaction,
    DeployAccountTransactionResponse,
    L1HandlerTransaction,
)
from starknet_py.net.schemas.common import (
    Felt,
    BlockStatusField,
    StatusField,
    NonPrefixedHex,
)

# pylint: disable=unused-argument
# pylint: disable=no-self-use


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
    contract_address = Felt(data_key="contract_address", required=True)
    calldata = fields.List(Felt(), data_key="calldata", required=True)
    entry_point_selector = Felt(data_key="entry_point_selector", load_default=None)
    nonce = Felt(data_key="nonce", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> InvokeTransaction:
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
        required=True,
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


class DeployTransactionResponseSchema(SentTransactionSchema):
    contract_address = Felt(data_key="address", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return DeployTransactionResponse(**data)


class DeployAccountTransactionResponseSchema(SentTransactionSchema):
    address = Felt(data_key="address", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return DeployAccountTransactionResponse(**data)


class StorageDiffSchema(Schema):
    address = Felt(data_key="address", required=True)
    key = Felt(data_key="key", required=True)
    value = Felt(data_key="value", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return StorageDiff(**data)


class DeployedContractSchema(Schema):
    address = Felt(data_key="address", required=True)
    class_hash = NonPrefixedHex(data_key="class_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return DeployedContract(**data)


class BlockStateUpdateSchema(Schema):
    block_hash = Felt(data_key="block_hash", required=True)
    new_root = NonPrefixedHex(data_key="new_root", required=True)
    old_root = NonPrefixedHex(data_key="old_root", required=True)
    state_diff = fields.Dict(
        keys=fields.String(), values=fields.Raw(), data_key="state_diff", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs):
        deployed_contracts = data["state_diff"]["deployed_contracts"]
        deployed_contracts = [
            cast(DeployedContract, DeployedContractSchema().load(contract))
            for contract in deployed_contracts
        ]

        storage_diffs = []
        for address, diffs in data["state_diff"]["storage_diffs"].items():
            for diff in diffs:
                storage_diff = StorageDiffSchema().load(
                    {"address": address, "key": diff["key"], "value": diff["value"]}
                )
                storage_diffs.append(storage_diff)

        declared_contracts = data["state_diff"]["declared_contracts"]
        declared_contracts = [
            int(declared_contract, 16) for declared_contract in declared_contracts
        ]

        del data["state_diff"]

        return BlockStateUpdate(
            **data,
            storage_diffs=storage_diffs,
            deployed_contracts=deployed_contracts,
            declared_contracts=declared_contracts,
        )


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


class DeclaredContractSchema(Schema):
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
    def make_dataclass(self, data, **kwargs) -> DeclaredContract:
        return DeclaredContract(**data)


class TransactionStatusSchema(Schema):
    transaction_status = StatusField(data_key="tx_status", required=True)
    block_hash = Felt(data_key="block_hash", allow_none=True)

    @post_load
    def make_result(self, data, **kwargs) -> TransactionStatusResponse:
        return TransactionStatusResponse(**data)
