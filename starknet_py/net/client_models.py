"""
Dataclasses representing responses from Starknet.
They need to stay backwards compatible for old transactions/blocks to be fetchable.
"""

from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, List, Optional, Union

from typing_extensions import Literal

from starknet_py.abi.shape import AbiDictList

Hash = Union[int, str]
Tag = Literal["pending", "latest"]


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
    Dataclass representing an event emitted by transaction.
    """

    from_address: int
    keys: List[int]
    data: List[int]


@dataclass
class EventsChunk:
    """
    Dataclass representing events returned by FullNodeClient.get_events method.
    """

    events: List[Event]
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
    price_in_strk: Optional[int]


@dataclass
class ResourceLimits:
    """
    Dataclass representing resource limits.
    """

    max_amount: int
    max_price_per_unit: int


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
    # Optional for DECLARE_V3 and DEPLOY_ACCOUNT_V3, where there is no `max_fee` field, but `l1_gas`
    max_fee: Optional[int]
    version: int

    def __post_init__(self):
        if self.__class__ == Transaction:
            raise TypeError("Cannot instantiate abstract Transaction class.")


@dataclass
class InvokeTransaction(Transaction):
    """
    Dataclass representing invoke transaction.
    """

    sender_address: int
    calldata: List[int]
    # This field is always None for transactions with version = 1
    entry_point_selector: Optional[int] = None
    nonce: Optional[int] = None


@dataclass
class DeclareTransaction(Transaction):
    """
    Dataclass representing declare transaction.
    """

    class_hash: int  # Responses to getBlock and getTransaction include the class hash
    sender_address: int
    compiled_class_hash: Optional[int] = None  # only in DeclareV2, hence Optional
    nonce: Optional[int] = None
    l1_gas: Optional[ResourceLimits] = None  # DECLARE_V3-only field, hence Optional


@dataclass
class DeployTransaction(Transaction):
    """
    Dataclass representing deploy transaction.
    """

    contract_address_salt: int
    constructor_calldata: List[int]
    class_hash: int
    l1_gas: Optional[
        ResourceLimits
    ] = None  # DEPLOY_ACCOUNT_V3-only field, hence Optional


@dataclass
class DeployAccountTransaction(Transaction):
    """
    Dataclass representing deploy account transaction.
    """

    contract_address_salt: int
    class_hash: int
    constructor_calldata: List[int]
    nonce: int


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

    NOT_RECEIVED = "NOT_RECEIVED"
    RECEIVED = "RECEIVED"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"
    REJECTED = "REJECTED"
    REVERTED = "REVERTED"
    SUCCEEDED = "SUCCEEDED"


class TransactionExecutionStatus(Enum):
    """
    Enum representing transaction execution statuses.
    """

    REJECTED = "REJECTED"
    REVERTED = "REVERTED"
    SUCCEEDED = "SUCCEEDED"


class TransactionFinalityStatus(Enum):
    """
    Enum representing transaction finality statuses.
    """

    NOT_RECEIVED = "NOT_RECEIVED"
    RECEIVED = "RECEIVED"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"


@dataclass
class ExecutionResources:
    """
    Dataclass representing the resources consumed by the transaction.
    """

    # pylint: disable=too-many-instance-attributes

    steps: int
    range_check_builtin_applications: int
    pedersen_builtin_applications: int
    poseidon_builtin_applications: int
    ec_op_builtin_applications: int
    ecdsa_builtin_applications: int
    bitwise_builtin_applications: int
    keccak_builtin_applications: int
    memory_holes: Optional[int] = None


# TODO (#1179): split into PendingTransactionReceipt and TransactionReceipt
@dataclass
class TransactionReceipt:
    """
    Dataclass representing details of sent transaction.
    """

    # pylint: disable=too-many-instance-attributes

    transaction_hash: int
    events: List[Event] = field(default_factory=list)
    l2_to_l1_messages: List[L2toL1Message] = field(default_factory=list)

    execution_status: Optional[TransactionExecutionStatus] = None
    finality_status: Optional[TransactionFinalityStatus] = None
    # TODO (#1179): remove status field once devnet is updated
    status: Optional[
        TransactionStatus
    ] = None  # replaced by execution and finality status in RPC v0.4.0-rc1

    type: Optional[TransactionType] = None
    contract_address: Optional[int] = None

    block_number: Optional[int] = None
    block_hash: Optional[int] = None
    actual_fee: int = 0
    # TODO (#1179): this field should be required
    execution_resources: Optional[ExecutionResources] = None

    message_hash: Optional[int] = None  # L1_HANDLER_TXN_RECEIPT-only

    rejection_reason: Optional[str] = None
    revert_reason: Optional[str] = None


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

    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"
    PROVEN = "PROVEN"


@dataclass
class PendingStarknetBlock:
    """
    Dataclass representing a pending block on Starknet.
    """

    transactions: List[Transaction]
    parent_block_hash: int
    timestamp: int
    sequencer_address: int
    # TODO (#1179): this field should be required
    l1_gas_price: Optional[ResourcePrice] = None
    # TODO (#1179): this field should be required
    starknet_version: Optional[str] = None


@dataclass
class PendingStarknetBlockWithTxHashes:
    """
    Dataclass representing a pending block on Starknet containing transaction hashes.
    """

    transactions: List[int]
    parent_block_hash: int
    timestamp: int
    sequencer_address: int
    # TODO (#1179): this field should be required
    l1_gas_price: Optional[ResourcePrice] = None
    # TODO (#1179): this field should be required
    starknet_version: Optional[str] = None


@dataclass
class StarknetBlockCommon:
    """
    Dataclass representing a block header.
    """

    # TODO (#1179): change that into composition
    # pylint: disable=too-many-instance-attributes

    block_hash: int
    parent_block_hash: int
    block_number: int
    root: int
    timestamp: int
    sequencer_address: int
    # TODO (#1179): this field should be required
    l1_gas_price: Optional[ResourcePrice]
    # TODO (#1179): this field should be required
    starknet_version: Optional[str]


@dataclass
class StarknetBlock(StarknetBlockCommon):
    """
    Dataclass representing a block on Starknet.
    """

    status: BlockStatus
    transactions: List[Transaction]


@dataclass
class StarknetBlockWithTxHashes(StarknetBlockCommon):
    """
    Dataclass representing a block on Starknet containing transaction hashes.
    """

    status: BlockStatus
    transactions: List[int]


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
    """
    Dataclass representing estimated fee.
    """

    overall_fee: int
    gas_price: int
    gas_usage: int


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
class PendingBlockStateUpdate:
    """
    Dataclass representing a pending change in state of a block.
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
class ContractClass:
    """
    Dataclass representing contract declared to Starknet.
    """

    program: dict
    entry_points_by_type: EntryPointsByType
    abi: Optional[AbiDictList] = None


@dataclass
class CompiledContract(ContractClass):
    """
    Dataclass representing ContractClass with required abi.
    """

    # abi is a required key in CompiledContractSchema,
    # default_factory is used, since abi in ContractClass is Optional
    # and otherwise, non-keyword arguments would follow keyword arguments
    abi: AbiDictList = field(default_factory=list)


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
class SierraContractClass:
    """
    Dataclass representing Cairo1 contract declared to Starknet
    """

    contract_class_version: str
    sierra_program: List[str]
    entry_points_by_type: SierraEntryPointsByType
    abi: Optional[str] = None


@dataclass
class SierraCompiledContract(SierraContractClass):
    """
    Dataclass representing SierraContractClass with required abi.
    """

    abi: str = field(default_factory=str)


@dataclass
class CasmClassEntryPoint:
    """
    Dataclass representing CasmClass entrypoint.
    """

    selector: int
    offset: int
    builtins: Optional[List[str]]


@dataclass
class CasmClassEntryPointsByType:
    """
    Dataclass representing CasmClass entrypoints by entry point type.
    """

    constructor: List[CasmClassEntryPoint]
    external: List[CasmClassEntryPoint]
    l1_handler: List[CasmClassEntryPoint]


@dataclass
class CasmClass:
    """
    Dataclass representing class compiled to Cairo assembly.
    """

    prime: int
    bytecode: List[int]
    hints: List[Any]
    pythonic_hints: List[Any]
    compiler_version: str
    entry_points_by_type: CasmClassEntryPointsByType


@dataclass
class TransactionStatusResponse:
    """
    Dataclass representing transaction status for the FullNodeClient.
    """

    finality_status: TransactionStatus
    execution_status: Optional[TransactionExecutionStatus] = None


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
    validate_invocation: Optional[FunctionInvocation] = None
    fee_transfer_invocation: Optional[FunctionInvocation] = None
    state_diff: Optional[StateDiff] = None


@dataclass
class DeclareTransactionTrace:
    """
    Dataclass representing a transaction trace of an DECLARE transaction.
    """

    validate_invocation: Optional[FunctionInvocation] = None
    fee_transfer_invocation: Optional[FunctionInvocation] = None
    state_diff: Optional[StateDiff] = None


@dataclass
class DeployAccountTransactionTrace:
    """
    Dataclass representing a transaction trace of an DEPLOY_ACCOUNT transaction.
    """

    constructor_invocation: FunctionInvocation
    validate_invocation: Optional[FunctionInvocation] = None
    fee_transfer_invocation: Optional[FunctionInvocation] = None
    state_diff: Optional[StateDiff] = None


@dataclass
class L1HandlerTransactionTrace:
    """
    Dataclass representing a transaction trace of an L1_HANDLER transaction.
    """

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
