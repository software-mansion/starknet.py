from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Any, Dict


@dataclass
class Event:
    from_address: int
    keys: List[int]
    data: List[int]


@dataclass
class FunctionCall:
    """
    Dataclass representing a call to a function
    """

    contract_address: int
    entry_point_selector: int
    calldata: List[int]


@dataclass
class L1toL2Message:
    l1_address: int
    l2_address: int
    payload: List[int]


@dataclass
class L2toL1Message:
    l2_address: int
    l1_address: int
    payload: List[int]


@dataclass
class Transaction:
    """
    Dataclass representing a transaction
    """

    hash: int
    contract_address: int
    entry_point_selector: int
    calldata: List[int]


class TransactionStatus(Enum):
    UNKNOWN = 0
    RECEIVED = auto()
    PENDING = auto()
    ACCEPTED_ON_L2 = auto()
    ACCEPTED_ON_L1 = auto()
    REJECTED = auto()


@dataclass
class TransactionReceipt:
    """
    Dataclass representing details of sent transaction
    """

    hash: int
    status: TransactionStatus
    events: List[Event]
    l1_to_l2_consumed_message: L1toL2Message
    l2_to_l1_messages: List[L2toL1Message]


@dataclass
class SentTransaction:
    hash: int
    code: str


class BlockStatus(Enum):
    """
    Enum representing block status
    """

    NOT_RECEIVED = 0
    RECEIVED = auto()
    PENDING = auto()
    REJECTED = auto()
    ACCEPTED_ON_L2 = auto()
    ACCEPTED_ON_L1 = auto()


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
class BlockState:
    """
    Dataclass representing a change in state of a block
    """

    block_hash: int
    root: int
    timestamp: int
    # TODO add proper diff dataclass
    diff: Any


@dataclass
class ContractCode:
    bytecode: List[int]
    abi: Dict[str, Any]
