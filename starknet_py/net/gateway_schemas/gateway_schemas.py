from marshmallow import Schema, fields, post_load, EXCLUDE
from marshmallow_oneofschema import OneOfSchema

from starknet_py.net.client_models import (
    ContractCode,
    StarknetBlock,
    L2toL1Message,
    L1toL2Message,
    SentTransactionResponse,
    ContractDiff,
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
)
from starknet_py.net.common_schemas.common_schemas import (
    Felt,
    BlockStatusField,
    StatusField,
    NonPrefixedHex,
)

# pylint: disable=unused-argument
# pylint: disable=no-self-use


class EventSchema(Schema):
    from_address = Felt(data_key="from_address")
    keys = fields.List(Felt(), data_key="keys")
    data = fields.List(Felt(), data_key="data")

    @post_load
    def make_dataclass(self, data, **kwargs) -> Event:
        return Event(**data)


class L1toL2MessageSchema(Schema):
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
    signature = fields.List(Felt(), data_key="signature", load_default=[])
    max_fee = Felt(load_default=0)


class InvokeTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address")
    calldata = fields.List(Felt(), data_key="calldata")
    entry_point_selector = Felt(data_key="entry_point_selector")

    @post_load
    def make_dataclass(self, data, **kwargs) -> InvokeTransaction:
        return InvokeTransaction(**data)


class DeployTransactionSchema(TransactionSchema):
    contract_address = Felt(data_key="contract_address")
    constructor_calldata = fields.List(Felt(), data_key="constructor_calldata")
    # class_hash = Felt(data_key="class_hash", load_default=0)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployTransaction:
        return DeployTransaction(**data)


class DeclareTransactionSchema(TransactionSchema):
    class_hash = Felt(data_key="class_hash")
    sender_address = Felt(data_key="sender_address")

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclareTransaction:
        return DeclareTransaction(**data)


class TypesOfTransactionsSchema(OneOfSchema):
    type_field = "type"
    type_schemas = {
        "INVOKE_FUNCTION": InvokeTransactionSchema,
        "DECLARE": DeclareTransactionSchema,
        "DEPLOY": DeployTransactionSchema,
    }


class TransactionReceiptSchema(Schema):
    hash = Felt(data_key="transaction_hash")
    status = StatusField(data_key="status")
    block_number = fields.Integer(data_key="block_number", load_default=None)
    version = fields.Integer(data_key="version", allow_none=True)
    actual_fee = Felt(data_key="actual_key", allow_none=True)
    rejection_reason = fields.String(
        data_key="transaction_rejection_reason", allow_none=True, load_default=None
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
        return TransactionReceipt(**data)


class ContractCodeSchema(Schema):
    bytecode = fields.List(Felt(), data_key="bytecode")
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
        fields.Nested(TypesOfTransactionsSchema(unknown=EXCLUDE)),
        data_key="transactions",
    )
    timestamp = fields.Integer(data_key="timestamp")

    @post_load
    def make_dataclass(self, data, **kwargs):
        return StarknetBlock(**data)


class BlockSingleTransactionTraceSchema(Schema):
    function_invocation = fields.Dict(
        keys=fields.String(), values=fields.Raw(), data_key="function_invocation"
    )
    signature = fields.List(Felt(), data_key="signature", load_default=[])
    transaction_hash = Felt(data_key="transaction_hash")

    @post_load
    def make_dataclass(self, data, **kwargs):
        return BlockSingleTransactionTrace(**data)


class BlockTransactionTracesSchema(Schema):
    traces = fields.List(
        fields.Nested(BlockSingleTransactionTraceSchema(unknown=EXCLUDE)),
        data_key="traces",
    )

    @post_load
    def make_dataclass(self, data, **kwargs):
        return BlockTransactionTraces(**data)


class EstimatedFeeSchema(Schema):
    overall_fee = fields.Integer(data_key="overall_fee")
    gas_price = fields.Integer(data_key="gas_price")
    gas_usage = fields.Integer(data_key="gas_usage")

    @post_load
    def make_dataclass(self, data, **kwargs):
        return EstimatedFee(**data)


class SentTransactionSchema(Schema):
    hash = Felt(data_key="transaction_hash")
    code = fields.String(data_key="code")
    address = Felt(data_key="address", allow_none=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return SentTransactionResponse(**data)


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

        declared_contracts = data["state_diff"]["declared_contracts"]
        declared_contracts = [
            int(declared_contract, 16) for declared_contract in declared_contracts
        ]

        del data["state_diff"]

        return BlockStateUpdate(
            **data,
            storage_diffs=storage_diffs,
            contract_diffs=contracts_diffs,
            declared_contracts=declared_contracts,
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


class DeclaredContractSchema(Schema):
    program = fields.Dict(
        keys=fields.String(), values=fields.Raw(allow_none=True), data_key="program"
    )
    entry_points_by_type = fields.Nested(
        EntryPointsByTypeSchema(), data_key="entry_points_by_type"
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeclaredContract:
        return DeclaredContract(**data)


class TransactionStatusSchema(Schema):
    transaction_status = StatusField(data_key="tx_status")
    block_hash = fields.Integer(data_key="block_hash", allow_none=True)

    @post_load
    def make_result(self, data, **kwargs) -> TransactionStatusResponse:
        return TransactionStatusResponse(**data)
