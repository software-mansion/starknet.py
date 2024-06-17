"""
TypedDict structures for TypedData
"""

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict, Union


class Parameter(TypedDict):
    """
    TypedDict representing a Parameter object
    """

    name: str
    type: str


class Revision(Enum):
    """
    Enum representing the revision of the specification to be used.
    """

    V0 = 0
    V1 = 1


class Domain(TypedDict):
    """
    TypedDict representing a domain object (both StarkNetDomain, StarknetDomain).
    """

    name: str
    version: str
    chainId: Union[str, int]
    revision: Optional[Union[str, int]]


class TypedData(TypedDict):
    """
    TypedDict representing a TypedData object
    """

    types: Dict[str, List[Parameter]]
    primaryType: str
    domain: Domain
    message: Dict[str, Any]
