from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import List, Any, Dict, Optional, Union, Iterable
from typing_extensions import Literal

from starkware.starknet.services.api.gateway.transaction import (
    InvokeFunction as IF,
    Transaction as T,
    ContractClass as CD,
    Deploy as D,
    Declare as DCL,
)


from starknet_py.utils.docs import as_our_module

InvokeFunction = as_our_module(IF)
StarknetTransaction = as_our_module(T)
ContractClass = as_our_module(CD)
Deploy = as_our_module(D)
Declare = as_our_module(DCL)


Hash = Union[int, str]
Tag = Literal["pending", "latest"]


@dataclass
class Call:
    to_addr: int
    selector: int
    calldata: List[int]


Calls = Union[Call, Iterable[Call]]


@dataclass
class Event:
    """
    Dataclass representing an event emited by transaction
    """

    from_address: int
    keys: List[int]
    data: List[int]


@dataclass
class L1toL2Message:
    """
    Dataclass representing a L1->L2 message
    """

    payload: List[int]
    l1_address: int
    l2_address: Optional[int] = None


@dataclass
class L2toL1Message:
    """
    Dataclass representing a L2->L1 message
    """

    payload: List[int]
    l1_address: int
    l2_address: Optional[int] = None


class TransactionType(Enum):
    """
    Enum representing transaction types
    """

    INVOKE = "INVOKE"
    DEPLOY = "DEPLOY"
    DECLARE = "DECLARE"


@dataclass
class Transaction(ABC):
    """
    Dataclass representing common attributes of all transactions
    """

    hash: int
    signature: List[int]
    max_fee: int

    def __post_init__(self):
        if self.__class__ == Transaction:
            raise TypeError("Cannot instantiate abstract Transaction class")


@dataclass
class InvokeTransaction(Transaction):
    """
    Dataclass representing invoke transaction
    """

    contract_address: int
    calldata: List[int]
    entry_point_selector: int


@dataclass
class DeclareTransaction(Transaction):
    """
    Dataclass representing declare transaction
    """

    class_hash: int
    sender_address: int


@dataclass
class DeployTransaction(Transaction):
    """
    Dataclass representing deploy transaction
    """

    contract_address: int
    constructor_calldata: List[int]
    # TODO add once RPC supports rpc transactions better
    # class_hash: Optional[int] = None


class TransactionStatus(Enum):
    """
    Enum representing transaction statuses
    """

    NOT_RECEIVED = "NOT_RECEIVED"
    RECEIVED = "RECEIVED"
    PENDING = "PENDING"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"
    REJECTED = "REJECTED"


@dataclass
class TransactionReceipt:
    """
    Dataclass representing details of sent transaction
    """

    # pylint: disable=too-many-instance-attributes

    hash: int
    status: TransactionStatus
    block_number: Optional[int] = None
    version: int = 0
    actual_fee: int = 0
    rejection_reason: Optional[str] = None

    events: List[Event] = None
    l2_to_l1_messages: List[L2toL1Message] = None
    l1_to_l2_consumed_message: Optional[L1toL2Message] = None


@dataclass
class SentTransactionResponse:
    """
    Dataclass representing a result of sending a transaction to starknet
    """

    transaction_hash: int
    code: Optional[str] = None


@dataclass
class DeclareTransactionResponse(SentTransactionResponse):
    """
    Dataclass representing a result of declaring a contract on starknet
    """

    class_hash: int = None


@dataclass
class DeployTransactionResponse(SentTransactionResponse):
    """
    Dataclass representing a result of deploying a contract to starknet
    """

    contract_address: int = None


class BlockStatus(Enum):
    """
    Enum representing block status
    """

    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"
    PROVEN = "PROVEN"


@dataclass
class StarknetBlock:
    """
    Dataclass representing a transaction on starknet
    """

    # pylint: disable=too-many-instance-attributes

    block_hash: int
    parent_block_hash: int
    block_number: int
    status: BlockStatus
    root: int
    transactions: List[Transaction]
    timestamp: int


@dataclass
class BlockSingleTransactionTrace:
    function_invocation: dict
    signature: List[int]
    transaction_hash: int


@dataclass
class BlockTransactionTraces:
    traces: List[BlockSingleTransactionTrace]


@dataclass
class StorageDiff:
    address: int
    key: int
    value: int


@dataclass
class EstimatedFee:
    overall_fee: int
    gas_price: int
    gas_usage: int


@dataclass
class ContractDiff:
    address: int
    contract_hash: int


@dataclass
class BlockStateUpdate:
    """
    Dataclass representing a change in state of a block
    """

    block_hash: int
    new_root: int
    old_root: int
    storage_diffs: List[StorageDiff]
    contract_diffs: List[ContractDiff]
    declared_contracts: List[int]


@dataclass
class ContractCode:
    """
    Dataclass representing contract deployed to starknet
    """

    bytecode: List[int]
    abi: List[Dict[str, Any]]


@dataclass
class EntryPoint:
    """
    Dataclass representing contract entry point
    """

    offset: int
    selector: int


@dataclass
class EntryPointsByType:
    """
    Dataclass representing contract class entrypoints by entry point type
    """

    constructor: List[EntryPoint]
    external: List[EntryPoint]
    l1_handler: List[EntryPoint]


@dataclass
class DeclaredContract:
    """
    Dataclass representing contract declared to starknet
    """

    program: dict
    entry_points_by_type: EntryPointsByType


@dataclass
class TransactionStatusResponse:
    block_hash: Optional[int]
    transaction_status: TransactionStatus
