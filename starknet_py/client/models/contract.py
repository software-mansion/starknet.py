from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from starknet_py.client.models.abi import Abi


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
    abi: Optional[Abi] = None
