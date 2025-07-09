"""
Dataclasses representing responses from Starknet.
They need to stay backwards compatible for old transactions/blocks to be fetchable.

If you encounter a ValidationError in the context of an RPC response, it is possible to disable validation.
This can be achieved by setting the environment variable, STARKNET_PY_MARSHMALLOW_UNKNOWN_EXCLUDE,
to true. Consequently, any unknown fields in response will be excluded.
"""

import datetime
import json
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Literal, Optional, Union, cast

from marshmallow import EXCLUDE

from starknet_py.abi.v0.shape import AbiDictList
from starknet_py.abi.v1.schemas import (
    ContractAbiEntrySchema as ContractAbiEntrySchemaV1,
)
from starknet_py.abi.v1.shape import AbiDictEntry as AbiDictEntryV1
from starknet_py.abi.v1.shape import AbiDictList as AbiDictListV1
from starknet_py.abi.v2.schemas import (
    ContractAbiEntrySchema as ContractAbiEntrySchemaV2,
)
from starknet_py.abi.v2.shape import AbiDictEntry as AbiDictEntryV2
from starknet_py.abi.v2.shape import AbiDictList as AbiDictListV2
from starknet_py.utils.constructor_args_translator import _is_abi_v2

# pylint: disable=too-many-lines

Hash = Union[int, str]
Tag = Literal["pre_confirmed", "latest"]
LatestTag = Literal["latest"]


@dataclass
class Call:
    """
    Dataclass representing a call to Starknet contract.
    """

    to_addr: int
    selector: int
    calldata: List[int]


Calls = Union[Call, Iterable[Call]]


@dataclass
class Event:
    """
    Dataclass representing a Starknet event.
    """

    from_address: int
    keys: List[int]
    data: List[int]


@dataclass
class EmittedEvent(Event):
    """
    Dataclass representing an event emitted by transaction.
    """

    transaction_hash: int
    block_hash: Optional[int] = None
    block_number: Optional[int] = None


@dataclass
class EventsChunk:
    """
    Dataclass representing events returned by FullNodeClient.get_events method.
    """

    events: List[EmittedEvent]
    continuation_token: Optional[str] = None


@dataclass
class L2toL1Message:
    """
    Dataclass representing a L2->L1 message.
    """

    payload: List[int]
    l2_address: int  # from_address in spec
    l1_address: int  # to_address in spec


@dataclass
class ResourcePrice:
    """
    Dataclass representing prices of L1 gas.
    """

    price_in_wei: int
    price_in_fri: int


@dataclass
class ResourceBounds:
    """
    Dataclass representing max amount and price of the resource that can be used in the transaction.
    """

    max_amount: int
    max_price_per_unit: int

    @staticmethod
    def init_with_zeros():
        return ResourceBounds(max_amount=0, max_price_per_unit=0)


@dataclass
class OutsideExecutionTimeBounds:
    """
    Dataclass representing time bounds within which outside execution
    transaction is valid and allowed to be executed.
    """

    execute_after: datetime.datetime
    execute_before: datetime.datetime

    @property
    def execute_after_timestamp(self) -> int:
        return int(self.execute_after.timestamp())

    @property
    def execute_before_timestamp(self) -> int:
        return int(self.execute_before.timestamp())


@dataclass
class ResourceBoundsMapping:
    """
    Dataclass representing resource limits that can be used in the transaction.
    """

    l1_gas: ResourceBounds
    l1_data_gas: ResourceBounds
    l2_gas: ResourceBounds

    @staticmethod
    def init_with_zeros():
        return ResourceBoundsMapping(
            l1_gas=ResourceBounds.init_with_zeros(),
            l1_data_gas=ResourceBounds.init_with_zeros(),
            l2_gas=ResourceBounds.init_with_zeros(),
        )


class PriceUnit(Enum):
    """
    Enum representing price unit types.
    """

    WEI = "WEI"
    FRI = "FRI"


@dataclass
class FeePayment:
    """
    Dataclass representing fee payment info as it appears in receipts.
    """

    amount: int
    unit: PriceUnit


class DAMode(Enum):
    """
    Specifies a storage domain in Starknet. Each domain has different guarantees regarding availability.
    """

    L1 = 0
    L2 = 1


class L1DAMode(Enum):
    BLOB = "BLOB"
    CALLDATA = "CALLDATA"


class TransactionType(Enum):
    """
    Enum representing transaction types.
    """

    INVOKE = "INVOKE"
    DECLARE = "DECLARE"
    DEPLOY_ACCOUNT = "DEPLOY_ACCOUNT"
    DEPLOY = "DEPLOY"
    L1_HANDLER = "L1_HANDLER"


@dataclass
class Transaction(ABC):
    """
    Dataclass representing common attributes of all transactions.
    """

    # Technically, RPC specification moved 'transaction_hash' out of the TXN object, but since it is always returned
    # together with the rest of the data, it remains here (but is still Optional just in case as spec says)
    hash: Optional[int]
    signature: List[int]
    version: int

    def __post_init__(self):
        if self.__class__ == Transaction:
            raise TypeError("Cannot instantiate abstract Transaction class.")


@dataclass
class DeprecatedTransaction(Transaction):
    """
    Dataclass representing common attributes of transactions v1 and v2.
    """

    max_fee: int

    def __post_init__(self):
        if self.__class__ == DeprecatedTransaction:
            raise TypeError("Cannot instantiate abstract DeprecatedTransaction class.")


@dataclass
class TransactionV3(Transaction):
    """
    Dataclass representing common attributes of all transactions v3.
    """

    resource_bounds: ResourceBoundsMapping
    paymaster_data: List[int]
    tip: int
    nonce_data_availability_mode: DAMode
    fee_data_availability_mode: DAMode

    def __post_init__(self):
        if self.__class__ == TransactionV3:
            raise TypeError("Cannot instantiate abstract TransactionV3 class.")


@dataclass
class InvokeTransactionV0(DeprecatedTransaction):
    """
    Dataclass representing invoke transaction v0.
    """

    calldata: List[int]
    contract_address: int
    entry_point_selector: int


@dataclass
class InvokeTransactionV1(DeprecatedTransaction):
    """
    Dataclass representing invoke transaction v1.

    .. deprecated:: 0.25.0
        This class is deprecated and will be removed in future versions.
        Use `starknet_py.net.client_models.InvokeTransactionV3` instead.
    """

    calldata: List[int]
    sender_address: int
    nonce: int


@dataclass
class InvokeTransactionV3(TransactionV3):
    """
    Dataclass representing invoke transaction v3.
    """

    calldata: List[int]
    sender_address: int
    nonce: int
    account_deployment_data: List[int]


@dataclass
class DeclareTransactionV0(DeprecatedTransaction):
    """
    Dataclass representing declare transaction v0.
    """

    sender_address: int
    class_hash: int


@dataclass
class DeclareTransactionV1(DeprecatedTransaction):
    """
    Dataclass representing declare transaction v1.

    .. deprecated:: 0.25.0
        This class is deprecated and will be removed in future versions.
        Use `starknet_py.net.client_models.DeclareTransactionV3` instead.
    """

    sender_address: int
    class_hash: int
    nonce: int


@dataclass
class DeclareTransactionV2(DeprecatedTransaction):
    """
    Dataclass representing declare transaction v2.

    .. deprecated:: 0.25.0
        This class is deprecated and will be removed in future versions.
        Use `starknet_py.net.client_models.DeclareTransactionV3` instead.
    """

    sender_address: int
    class_hash: int
    compiled_class_hash: int
    nonce: int


@dataclass
class DeclareTransactionV3(TransactionV3):
    """
    Dataclass representing declare transaction v3.
    """

    sender_address: int
    class_hash: int
    compiled_class_hash: int
    nonce: int
    account_deployment_data: List[int]


@dataclass
class DeployTransaction(Transaction):
    """
    Dataclass representing deploy transaction.
    """

    contract_address_salt: int
    constructor_calldata: List[int]
    class_hash: int


@dataclass
class DeployAccountTransactionV1(DeprecatedTransaction):
    """
    Dataclass representing deploy account transaction v1.

    .. deprecated:: 0.25.0
        This class is deprecated and will be removed in future versions.
        Use `starknet_py.net.client_models.DeployAccountTransactionV3` instead.
    """

    nonce: int
    contract_address_salt: int
    constructor_calldata: List[int]
    class_hash: int


@dataclass
class DeployAccountTransactionV3(TransactionV3):
    """
    Dataclass representing deploy account transaction v3.
    """

    nonce: int
    contract_address_salt: int
    constructor_calldata: List[int]
    class_hash: int


@dataclass
class L1HandlerTransaction(Transaction):
    """
    Dataclass representing l1 handler transaction.
    """

    contract_address: int
    calldata: List[int]
    entry_point_selector: int
    nonce: int


class TransactionStatus(Enum):
    """
    Enum representing transaction statuses.
    """

    RECEIVED = "RECEIVED"
    CANDIDATE = "CANDIDATE"
    PRE_CONFIRMED = "PRE_CONFIRMED"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"


class TransactionExecutionStatus(Enum):
    """
    Enum representing transaction execution statuses.
    """

    SUCCEEDED = "SUCCEEDED"
    REVERTED = "REVERTED"


class TransactionFinalityStatus(Enum):
    """
    Enum representing transaction finality statuses.
    """

    PRE_CONFIRMED = "PRE_CONFIRMED"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"


@dataclass
class InnerCallExecutionResources:
    """
    Dataclass representing the resource consumed by an inner call (does not account for state diffs).
    """

    l1_gas: int
    l2_gas: int


@dataclass
class ExecutionResources:
    """
    Dataclass representing the resources consumed by the transaction, includes both computation and data.
    """

    l1_gas: int
    l1_data_gas: int
    l2_gas: int


# TODO (#1219): split into PendingTransactionReceipt and TransactionReceipt
@dataclass
class TransactionReceipt:
    """
    Dataclass representing details of sent transaction.
    """

    # pylint: disable=too-many-instance-attributes

    transaction_hash: int
    execution_status: TransactionExecutionStatus
    finality_status: TransactionFinalityStatus
    execution_resources: ExecutionResources
    actual_fee: FeePayment
    type: TransactionType

    events: List[Event] = field(default_factory=list)
    messages_sent: List[L2toL1Message] = field(default_factory=list)

    block_number: Optional[int] = None
    block_hash: Optional[int] = None

    contract_address: Optional[int] = None  # DEPLOY_ACCOUNT_TXN_RECEIPT only
    message_hash: Optional[int] = None  # L1_HANDLER_TXN_RECEIPT only

    revert_reason: Optional[str] = None


@dataclass
class TransactionWithReceipt:
    transaction: Transaction
    receipt: TransactionReceipt


@dataclass
class SentTransactionResponse:
    """
    Dataclass representing a result of sending a transaction to Starknet.
    """

    transaction_hash: int
    code: Optional[str] = None


@dataclass
class DeclareTransactionResponse(SentTransactionResponse):
    """
    Dataclass representing a result of declaring a contract on Starknet.
    """

    class_hash: int = 0


@dataclass
class DeployAccountTransactionResponse(SentTransactionResponse):
    """
    Dataclass representing a result of deploying an account contract to Starknet.
    """

    address: int = 0


class BlockStatus(Enum):
    """
    Enum representing block status.
    """

    PRE_CONFIRMED = "PRE_CONFIRMED"
    REJECTED = "REJECTED"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"


@dataclass
class PreConfirmedBlockHeader:
    # pylint: disable=too-many-instance-attributes
    block_number: int
    timestamp: int
    sequencer_address: int
    l1_gas_price: ResourcePrice
    l2_gas_price: ResourcePrice
    l1_data_gas_price: ResourcePrice
    l1_da_mode: L1DAMode
    starknet_version: str


@dataclass
class PreConfirmedStarknetBlock(PreConfirmedBlockHeader):
    """
    Dataclass representing a pre-confirmed block on Starknet.
    """

    transactions: List[Transaction]


@dataclass
class PreConfirmedStarknetBlockWithTxHashes(PreConfirmedBlockHeader):
    """
    Dataclass representing a pre_confirmed block on Starknet containing transaction hashes.
    """

    transactions: List[int]


@dataclass
class PreConfirmedStarknetBlockWithReceipts(PreConfirmedBlockHeader):
    """
    Dataclass representing a pre_confirmed block on Starknet with txs and receipts result
    """

    transactions: List[TransactionWithReceipt]


@dataclass
class BlockHeader:
    """
    Dataclass representing a block header.
    """

    # pylint: disable=too-many-instance-attributes

    block_hash: int
    parent_hash: int
    block_number: int
    new_root: int
    timestamp: int
    sequencer_address: int
    l1_gas_price: ResourcePrice
    l2_gas_price: ResourcePrice
    l1_data_gas_price: ResourcePrice
    l1_da_mode: L1DAMode
    starknet_version: str


@dataclass
class StarknetBlock(BlockHeader):
    """
    Dataclass representing a block on Starknet.
    """

    status: BlockStatus
    transactions: List[Transaction]


@dataclass
class StarknetBlockWithTxHashes(BlockHeader):
    """
    Dataclass representing a block on Starknet containing transaction hashes.
    """

    status: BlockStatus
    transactions: List[int]


@dataclass
class StarknetBlockWithReceipts(BlockHeader):
    """
    Dataclass representing a block on Starknet with txs and receipts result
    """

    status: BlockStatus
    transactions: List[TransactionWithReceipt]


@dataclass
class BlockHashAndNumber:
    block_hash: int
    block_number: int


@dataclass
class SyncStatus:
    starting_block_hash: int
    starting_block_num: int
    current_block_hash: int
    current_block_num: int
    highest_block_hash: int
    highest_block_num: int


@dataclass
class StorageEntry:
    """
    Dataclass representing single change in the storage.
    """

    key: int
    value: int


@dataclass
class StorageDiffItem:
    """
    Dataclass representing all storage changes for the contract.
    """

    address: int
    storage_entries: List[StorageEntry]


@dataclass
class EstimatedFee:
    # pylint: disable=too-many-instance-attributes
    """
    Dataclass representing estimated fee.
    """

    l1_gas_consumed: int
    l1_gas_price: int
    l2_gas_consumed: int
    l2_gas_price: int
    l1_data_gas_consumed: int
    l1_data_gas_price: int
    overall_fee: int
    unit: PriceUnit

    def to_resource_bounds(
        self, amount_multiplier=1.5, unit_price_multiplier=1.5
    ) -> ResourceBoundsMapping:
        """
        Converts estimated fee to resource bounds with applied multipliers.

        :param amount_multiplier: Multiplier for max amount, defaults to 1.5.
        :param unit_price_multiplier: Multiplier for max price per unit, defaults to 1.5.
        :return: Resource bounds with applied multipliers.
        """

        l1_resource_bounds = ResourceBounds(
            max_amount=int(self.l1_gas_consumed * amount_multiplier),
            max_price_per_unit=int(self.l1_gas_price * unit_price_multiplier),
        )

        l2_resource_bounds = ResourceBounds(
            max_amount=int(self.l2_gas_consumed * amount_multiplier),
            max_price_per_unit=int(self.l2_gas_price * unit_price_multiplier),
        )

        l1_data_resource_bounds = ResourceBounds(
            max_amount=int(self.l1_data_gas_consumed * amount_multiplier),
            max_price_per_unit=int(self.l1_data_gas_price * unit_price_multiplier),
        )

        return ResourceBoundsMapping(
            l1_gas=l1_resource_bounds,
            l2_gas=l2_resource_bounds,
            l1_data_gas=l1_data_resource_bounds,
        )

    def calculate_overall_fee(self):
        return (
            self.l1_gas_consumed * self.l1_gas_price
            + self.l2_gas_consumed * self.l2_gas_price
            + self.l1_data_gas_consumed * self.l1_data_gas_price
        )


@dataclass
class DeployedContract:
    """
    Dataclass representing basic data of the deployed contract.
    """

    address: int
    class_hash: int


@dataclass
class ContractsNonce:
    """
    Dataclass representing nonce of the contract.
    """

    contract_address: int
    nonce: int


@dataclass
class DeclaredContractHash:
    """
    Dataclass containing hashes of the declared contract.
    """

    class_hash: int
    compiled_class_hash: int


@dataclass
class ReplacedClass:
    """
    Dataclass representing new class_hash of the contract.
    """

    contract_address: int
    class_hash: int


@dataclass
class StateDiff:
    """
    Dataclass representing state changes in the block.
    """

    storage_diffs: List[StorageDiffItem]
    deprecated_declared_classes: List[int]
    declared_classes: List[DeclaredContractHash]
    deployed_contracts: List[DeployedContract]
    replaced_classes: List[ReplacedClass]
    nonces: List[ContractsNonce]


@dataclass
class BlockStateUpdate:
    """
    Dataclass representing a change in state of a block.
    """

    block_hash: int
    new_root: int
    old_root: int
    state_diff: StateDiff


@dataclass
class PreConfirmedBlockStateUpdate:
    """
    Dataclass representing a pre_confirmed change in state of a block.
    """

    old_root: int
    state_diff: StateDiff


@dataclass
class EntryPoint:
    """
    Dataclass representing contract entry point.
    """

    offset: int
    selector: int


@dataclass
class EntryPointsByType:
    """
    Dataclass representing contract class entrypoints by entry point type.
    """

    constructor: List[EntryPoint]
    external: List[EntryPoint]
    l1_handler: List[EntryPoint]


@dataclass
class _DeprecatedContract:
    """
    Dataclass representing contract declared on Starknet.
    """

    program: dict
    entry_points_by_type: EntryPointsByType


@dataclass
class DeprecatedContractClass(_DeprecatedContract):
    """
    Dataclass representing contract declared on Starknet.
    """

    abi: Optional[AbiDictList] = None


@dataclass
class DeprecatedCompiledContract(_DeprecatedContract):
    """
    Dataclass representing ContractClass with required abi.
    """

    # abi is a required key in CompiledContractSchema,
    # default_factory is used, since abi in ContractClass is Optional
    # and otherwise, non-keyword arguments would follow keyword arguments
    abi: AbiDictList = field(default_factory=list)

    def convert_to_deprecated_contract_class(self) -> DeprecatedContractClass:
        """
        Converts an instance of DeprecatedCompiledContract to DeprecatedContractClass.
        """
        return DeprecatedContractClass(
            program=self.program,
            entry_points_by_type=self.entry_points_by_type,
            abi=self.abi,
        )


@dataclass
class SierraEntryPoint:
    """
    Dataclass representing contract entry point
    """

    function_idx: int
    selector: int


@dataclass
class SierraEntryPointsByType:
    """
    Dataclass representing contract class entrypoints by entry point type
    """

    constructor: List[SierraEntryPoint]
    external: List[SierraEntryPoint]
    l1_handler: List[SierraEntryPoint]


@dataclass
class _SierraContract:

    contract_class_version: str
    sierra_program: List[int]
    entry_points_by_type: SierraEntryPointsByType


@dataclass
class SierraContractClass(_SierraContract):
    """
    Dataclass representing Cairo1 contract declared on Starknet
    """

    abi: Optional[str] = None

    @property
    def parsed_abi(self) -> Union[AbiDictListV2, AbiDictListV1]:
        if self.abi is None:
            return []

        load_abi: List = json.loads(self.abi)

        if _is_abi_v2(load_abi):
            return [
                cast(
                    AbiDictEntryV2,
                    ContractAbiEntrySchemaV2(unknown=EXCLUDE).load(entry),
                )
                for entry in load_abi
            ]

        return [
            cast(AbiDictEntryV1, ContractAbiEntrySchemaV1(unknown=EXCLUDE).load(entry))
            for entry in load_abi
        ]


@dataclass
class SierraCompiledContract(_SierraContract):
    """
    Dataclass representing SierraContractClass with required abi.
    """

    abi: str = field(default_factory=str)

    @property
    def parsed_abi(self) -> Union[AbiDictListV2, AbiDictListV1]:
        load_abi: List = json.loads(self.abi)

        if _is_abi_v2(load_abi):
            return [
                cast(
                    AbiDictEntryV2,
                    ContractAbiEntrySchemaV2(unknown=EXCLUDE).load(entry),
                )
                for entry in load_abi
            ]

        return [
            cast(AbiDictEntryV1, ContractAbiEntrySchemaV1(unknown=EXCLUDE).load(entry))
            for entry in load_abi
        ]

    def convert_to_sierra_contract_class(self) -> SierraContractClass:
        """
        Converts an instance of SierraCompiledContract to SierraContractClass.
        """
        return SierraContractClass(
            contract_class_version=self.contract_class_version,
            sierra_program=self.sierra_program,
            entry_points_by_type=self.entry_points_by_type,
            abi=self.abi,
        )


@dataclass
class CasmClassEntryPoint:
    """
    Dataclass representing CasmClass entrypoint.
    """

    selector: int
    offset: int
    builtins: List[str]


@dataclass
class CasmClassEntryPointsByType:
    """
    Dataclass representing CasmClass entrypoints by entry point type.
    """

    constructor: List[CasmClassEntryPoint]
    external: List[CasmClassEntryPoint]
    l1_handler: List[CasmClassEntryPoint]


@dataclass
class TransactionStatusResponse:
    """
    Dataclass representing transaction status for the FullNodeClient.
    """

    finality_status: TransactionStatus
    execution_status: Optional[TransactionExecutionStatus] = None
    failure_reason: Optional[str] = None


# ------------------------------- Trace API dataclasses -------------------------------


@dataclass
class OrderedEvent:
    """
    Dataclass representing an event alongside its order within the transaction.
    """

    keys: List[int]
    data: List[int]
    order: int


@dataclass
class OrderedMessage:
    """
    Dataclass representing a message alongside its order within the transaction.
    """

    payload: List[int]
    l2_address: int  # from_address in spec
    l1_address: int  # to_address in spec
    order: int


class SimulationFlag(str, Enum):
    """
    Enum class representing possible simulation flags for trace API.
    """

    SKIP_VALIDATE = "SKIP_VALIDATE"
    SKIP_FEE_CHARGE = "SKIP_FEE_CHARGE"


class EntryPointType(Enum):
    """
    Enum class representing entry point types.
    """

    EXTERNAL = "EXTERNAL"
    L1_HANDLER = "L1_HANDLER"
    CONSTRUCTOR = "CONSTRUCTOR"


class CallType(Enum):
    """
    Enum class representing call types.
    """

    DELEGATE = "DELEGATE"
    LIBRARY_CALL = "LIBRARY_CALL"
    CALL = "CALL"


@dataclass
class FunctionInvocation:
    """
    Dataclass representing an invocation of a function.
    """

    # pylint: disable=too-many-instance-attributes
    contract_address: int
    entry_point_selector: int
    calldata: List[int]
    caller_address: int
    class_hash: int
    entry_point_type: EntryPointType
    call_type: CallType
    result: List[int]
    calls: List["FunctionInvocation"]
    events: List[OrderedEvent]
    messages: List[OrderedMessage]
    execution_resources: InnerCallExecutionResources
    is_reverted: bool


@dataclass
class RevertedFunctionInvocation:
    """
    Dataclass representing revert reason for the transaction.
    """

    revert_reason: str


@dataclass
class InvokeTransactionTrace:
    """
    Dataclass representing a transaction trace of an INVOKE transaction.
    """

    execute_invocation: Union[FunctionInvocation, RevertedFunctionInvocation]
    execution_resources: ExecutionResources
    validate_invocation: Optional[FunctionInvocation] = None
    fee_transfer_invocation: Optional[FunctionInvocation] = None
    state_diff: Optional[StateDiff] = None


@dataclass
class DeclareTransactionTrace:
    """
    Dataclass representing a transaction trace of an DECLARE transaction.
    """

    execution_resources: ExecutionResources
    validate_invocation: Optional[FunctionInvocation] = None
    fee_transfer_invocation: Optional[FunctionInvocation] = None
    state_diff: Optional[StateDiff] = None


@dataclass
class DeployAccountTransactionTrace:
    """
    Dataclass representing a transaction trace of an DEPLOY_ACCOUNT transaction.
    """

    constructor_invocation: FunctionInvocation
    execution_resources: ExecutionResources
    validate_invocation: Optional[FunctionInvocation] = None
    fee_transfer_invocation: Optional[FunctionInvocation] = None
    state_diff: Optional[StateDiff] = None


@dataclass
class L1HandlerTransactionTrace:
    """
    Dataclass representing a transaction trace of an L1_HANDLER transaction.
    """

    execution_resources: ExecutionResources
    function_invocation: FunctionInvocation
    state_diff: Optional[StateDiff] = None


TransactionTrace = Union[
    InvokeTransactionTrace,
    DeclareTransactionTrace,
    DeployAccountTransactionTrace,
    L1HandlerTransactionTrace,
]


@dataclass
class SimulatedTransaction:
    """
    Dataclass representing a simulated transaction returned by `starknet_simulateTransactions` method.
    """

    transaction_trace: TransactionTrace
    fee_estimation: EstimatedFee


@dataclass
class BlockTransactionTrace:
    """
    Dataclass representing a single transaction trace in a block.
    """

    transaction_hash: int
    trace_root: TransactionTrace


@dataclass
class BinaryNode:
    """
    Dataclass representing an internal node whose both children are non-zero.
    """

    left: int
    right: int


@dataclass
class EdgeNode:
    """
    Dataclass representing a path to the highest non-zero descendant node.
    """

    path: int
    length: int
    child: int


MerkleNode = Union[BinaryNode, EdgeNode]


@dataclass
class NodeHashToNodeMappingItem:
    node_hash: int
    node: MerkleNode


NodeHashToNodeMapping = List[NodeHashToNodeMappingItem]


@dataclass
class ContractsStorageKeys:
    """
    Dataclass representing a pair of contract address and storage keys.
    """

    contract_address: int
    storage_keys: List[int]


@dataclass
class ContractLeafData:
    nonce: int
    class_hash: int
    storage_root: Optional[int]


@dataclass
class GlobalRoots:
    contracts_tree_root: int
    classes_tree_root: int
    block_hash: int


@dataclass
class ContractsProof:
    nodes: NodeHashToNodeMapping
    contract_leaves_data: List[ContractLeafData]


@dataclass
class StorageProofResponse:
    """
    Dataclass representing a response to a storage proof request.
    """

    classes_proof: NodeHashToNodeMapping
    contracts_proof: ContractsProof
    contracts_storage_proofs: List[NodeHashToNodeMapping]
    global_roots: GlobalRoots


class MessageFinalityStatus(Enum):
    """
    Enum representing transaction statuses.
    """

    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"


@dataclass
class MessageStatus:
    transaction_hash: int
    finality_status: MessageFinalityStatus
    execution_status: TransactionExecutionStatus
    failure_reason: Optional[str] = None


@dataclass
class OutsideExecution:
    """
    Dataclass representing an outside execution.
    (SNIP-9)[https://github.com/starknet-io/SNIPs/blob/main/SNIPS/snip-9.md]
    """

    caller: int
    nonce: int
    execute_after: int
    execute_before: int
    calls: List[Call]

    # TODO(#1537): Use serialiser to convert to ABI dict.
    def to_abi_dict(self) -> Dict:
        """
        Returns a dictionary that can be serialized (compiled) into calldata
        using StructSerializer
        """
        return {
            "caller": self.caller,
            "nonce": self.nonce,
            "execute_after": self.execute_after,
            "execute_before": self.execute_before,
            "calls": [
                {
                    "to": call.to_addr,
                    "selector": call.selector,
                    "calldata": call.calldata,
                }
                for call in self.calls
            ],
        }
