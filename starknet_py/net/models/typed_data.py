"""
TypedDict structures for TypedData
"""

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict, Union


class ParameterDict(TypedDict):
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

    @classmethod
    def _missing_(cls, value):
        raise ValueError("Allowed revision values are 0 and 1.")


class DomainDict(TypedDict):
    """
    TypedDict representing a domain object (both StarkNetDomain, StarknetDomain).
    """

    name: str
    version: str
    chainId: Union[str, int]
    revision: Optional[Revision]


class TypedDataDict(TypedDict):
    """
    TypedDict representing a TypedData object
    """

    types: Dict[str, List[ParameterDict]]
    primaryType: str
    domain: DomainDict
    message: Dict[str, Any]
