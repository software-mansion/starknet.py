from dataclasses import dataclass
from enum import Enum
from typing import List, Any, Dict, Optional, Union
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

    l1_address: int
    l2_address: int
    payload: List[int]


@dataclass
class L2toL1Message:
    """
    Dataclass representing a L2->L1 message
    """

    l2_address: int
    l1_address: int
    payload: List[int]


class TransactionType(Enum):
    """
    Enum representing transaction types
    """

    INVOKE = "INVOKE"
    DEPLOY = "DEPLOY"
    DELCLARE = "DECLARE"


@dataclass
class Transaction:
    """
    Dataclass representing a transaction
    """

    # pylint: disable=too-many-instance-attributes
    hash: int
    contract_address: int
    calldata: List[int]
    entry_point_selector: int
    transaction_type: TransactionType
    signature: List[int]
    version: int = 0
    max_fee: int = 0


class TransactionStatus(Enum):
    """
    Enum representing transaction statuses
    """

    UNKNOWN = "UNKNOWN"
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
    events: List[Event]
    l2_to_l1_messages: List[L2toL1Message]
    l1_to_l2_consumed_message: Optional[L1toL2Message] = None
    block_number: Optional[int] = None
    version: int = 0
    actual_fee: int = 0
    transaction_rejection_reason: Optional[str] = None


@dataclass
class SentTransaction:
    """
    Dataclass representing a result of sending a transaction to starknet
    """

    hash: int
    code: str
    address: Optional[int] = None


class BlockStatus(Enum):
    """
    Enum representing block status
    """

    NOT_RECEIVED = "NOT_RECEIVED"
    RECEIVED = "RECEIVED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACCEPTED_ON_L2 = "ACCEPTED_ON_L2"
    ACCEPTED_ON_L1 = "ACCEPTED_ON_L1"


@dataclass
class StarknetBlock:
    """
    Dataclass representing a transaction on starknet
    """

    block_hash: int
    parent_block_hash: int
    block_number: int
    status: BlockStatus
    root: int
    transactions: List[Transaction]
    timestamp: int


@dataclass
class StorageDiff:
    address: int
    key: int
    value: int


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
