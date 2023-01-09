from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union


@dataclass
class StructMember:
    """
    Dataclass representing struct member
    """

    name: str
    type: str
    offset: int


@dataclass
class TypedParameter:
    """
    Dataclass representing typed parameter
    """

    name: str
    type: str


@dataclass
class FunctionAbiEntry:
    """
    Dataclass representing function abi entry
    """

    name: str
    type: str
    inputs: List[TypedParameter]
    outputs: List[TypedParameter]
    stateMutability: Optional[str] = None  # pylint: disable=invalid-name


@dataclass
class EventAbiEntry:
    """
    Dataclass representing event abi entry
    """

    name: str
    type: str
    keys: List[TypedParameter]
    data: List[TypedParameter]


@dataclass
class StructAbiEntry:
    """
    Dataclass representing struct abi entry
    """

    name: str
    type: str
    size: List[TypedParameter]
    members: List[StructMember]


Abi = List[Dict[str, Any]]
ContractAbiEntry = Union[FunctionAbiEntry, EventAbiEntry, StructAbiEntry]
