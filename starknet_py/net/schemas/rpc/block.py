from marshmallow import fields, post_load

from starknet_py.net.client_models import (
    BlockHashAndNumber,
    BlockStateUpdate,
    ContractsNonce,
    DeclaredContractHash,
    DeployedContract,
    PendingBlockStateUpdate,
    PendingStarknetBlock,
    PendingStarknetBlockWithReceipts,
    PendingStarknetBlockWithTxHashes,
    ReplacedClass,
    ResourcePrice,
    StarknetBlock,
    StarknetBlockWithReceipts,
    StarknetBlockWithTxHashes,
    StateDiff,
    StorageDiffItem,
)
from starknet_py.net.schemas.common import (
    BlockStatusField,
    Felt,
    L1DAModeField,
    NonPrefixedHex,
    StorageEntrySchema,
)
from starknet_py.net.schemas.rpc.transactions import (
    TransactionWithReceiptSchema,
    TypesOfTransactionsSchema,
)
from starknet_py.utils.schema import Schema


class ResourcePriceSchema(Schema):
    price_in_fri = Felt(data_key="price_in_fri", required=True)
    price_in_wei = Felt(data_key="price_in_wei", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ResourcePrice:
        return ResourcePrice(**data)


class PendingBlockHeaderSchema(Schema):
    parent_hash = Felt(data_key="parent_hash", required=True)
    timestamp = fields.Integer(data_key="timestamp", required=True)
    sequencer_address = Felt(data_key="sequencer_address", required=True)
    l1_gas_price = fields.Nested(
        ResourcePriceSchema(), data_key="l1_gas_price", required=True
    )
    l1_data_gas_price = fields.Nested(
        ResourcePriceSchema(), data_key="l1_data_gas_price", required=True
    )
    l1_da_mode = L1DAModeField(data_key="l1_da_mode", required=True)
    starknet_version = fields.String(data_key="starknet_version", required=True)


class BlockHeaderSchema(Schema):
    block_hash = Felt(data_key="block_hash", required=True)
    parent_hash = Felt(data_key="parent_hash", required=True)
    block_number = fields.Integer(data_key="block_number", required=True)
    new_root = Felt(data_key="new_root", required=True)
    timestamp = fields.Integer(data_key="timestamp", required=True)
    sequencer_address = Felt(data_key="sequencer_address", required=True)
    l1_gas_price = fields.Nested(
        ResourcePriceSchema(), data_key="l1_gas_price", required=True
    )
    l1_data_gas_price = fields.Nested(
        ResourcePriceSchema(), data_key="l1_data_gas_price", required=True
    )
    l1_da_mode = L1DAModeField(data_key="l1_da_mode", required=True)
    starknet_version = fields.String(data_key="starknet_version", required=True)


class BlockHashAndNumberSchema(Schema):
    block_hash = Felt(data_key="block_hash", required=True)
    block_number = fields.Integer(data_key="block_number", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> BlockHashAndNumber:
        return BlockHashAndNumber(**data)


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
        return BlockStateUpdate(**data)


class PendingBlockStateUpdateSchema(Schema):
    old_root = Felt(data_key="old_root", required=True)
    state_diff = fields.Nested(StateDiffSchema(), data_key="state_diff", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> PendingBlockStateUpdate:
        return PendingBlockStateUpdate(**data)


class PendingStarknetBlockWithTxHashesSchema(PendingBlockHeaderSchema):
    transactions = fields.List(Felt(), data_key="transactions", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> PendingStarknetBlockWithTxHashes:
        return PendingStarknetBlockWithTxHashes(**data)


class StarknetBlockWithTxHashesSchema(BlockHeaderSchema):
    status = BlockStatusField(data_key="status", required=True)
    transactions = fields.List(Felt(), data_key="transactions", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> StarknetBlockWithTxHashes:
        return StarknetBlockWithTxHashes(**data)


class StarknetBlockWithReceiptsSchema(BlockHeaderSchema):
    status = BlockStatusField(data_key="status", required=True)
    transactions = fields.List(
        fields.Nested(TransactionWithReceiptSchema()),
        data_key="transactions",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> StarknetBlockWithReceipts:
        return StarknetBlockWithReceipts(**data)


class PendingStarknetBlockSchema(PendingBlockHeaderSchema):
    transactions = fields.List(
        fields.Nested(TypesOfTransactionsSchema()),
        data_key="transactions",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> PendingStarknetBlock:
        return PendingStarknetBlock(**data)


class StarknetBlockSchema(BlockHeaderSchema):
    status = BlockStatusField(data_key="status", required=True)
    transactions = fields.List(
        fields.Nested(TypesOfTransactionsSchema()),
        data_key="transactions",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> StarknetBlock:
        return StarknetBlock(**data)


class PendingStarknetBlockWithReceiptsSchema(PendingBlockHeaderSchema):
    transactions = fields.List(
        fields.Nested(TransactionWithReceiptSchema()),
        data_key="transactions",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> PendingStarknetBlockWithReceipts:
        return PendingStarknetBlockWithReceipts(**data)
