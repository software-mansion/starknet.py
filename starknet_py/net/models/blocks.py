from dataclasses import dataclass
from enum import Enum
from typing import List, Union
from typing_extensions import Literal

from starknet_py.net.models.contracts import DeployedContract
from starknet_py.net.models.transaction_payloads import Transaction


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
    Dataclass representing a block on starknet
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
class GatewayBlock(StarknetBlock):
    """
    Dataclass representing a block from the starknet gateway
    """

    gas_price: int


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
class StateDiff:
    deployed_contracts: List[DeployedContract]
    storage_diffs: List[StorageDiff]
    declared_contracts: List[int]


@dataclass
class BlockStateUpdate:
    """
    Dataclass representing a change in state of a block
    """

    block_hash: int
    new_root: int
    old_root: int
    storage_diffs: List[StorageDiff]
    deployed_contracts: List[DeployedContract]
    declared_contracts: List[int]


Hash = Union[int, str]
Tag = Literal["pending", "latest"]
