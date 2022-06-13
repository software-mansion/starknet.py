from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Any, Dict, Optional, Union

from starkware.starknet.services.api.gateway.transaction import (
    InvokeFunction as IF,
    Transaction as T,
    ContractClass as CD,
    Deploy as D,
)


from starknet_py.utils.docs import as_our_module

InvokeFunction = as_our_module(IF)
StarknetTransaction = as_our_module(T)
ContractDefinition = as_our_module(CD)
Deploy = as_our_module(D)


Hash = Union[int, str]


@dataclass
class Event:
    from_address: int
    keys: List[int]
    data: List[int]


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


class TransactionType(Enum):
    INVOKE = 0
    DEPLOY = auto()


@dataclass
class Transaction:
    """
    Dataclass representing a transaction
    """

    hash: int
    contract_address: int
    calldata: List[int]
    entry_point_selector: int
    transaction_type: TransactionType
    version: int = 0
    max_fee: int = 0


class TransactionStatus(Enum):
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

    hash: int
    status: TransactionStatus
    events: List[Event]
    l2_to_l1_messages: List[L2toL1Message]
    l1_to_l2_consumed_message: Optional[L1toL2Message] = None
    block_number: Optional[int] = None
    version: int = 0
    actual_fee: int = 0
    transaction_rejection_reason: str = ""


@dataclass
class SentTransaction:
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
    abi: List[Dict[str, Any]]
