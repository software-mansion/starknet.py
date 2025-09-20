"""
TypedDict structures for TypedData
"""

import sys
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict

if sys.version_info < (3, 11):
    from typing_extensions import NotRequired
else:
    from typing import NotRequired


class Revision(Enum):
    """
    Enum representing the revision of the specification to be used.
    """

    V0 = 0
    V1 = 1


class ParameterDict(TypedDict):
    """
    TypedDict representing a Parameter object
    """

    name: str
    type: str
    contains: NotRequired[str]


class DomainDict(TypedDict):
    """
    TypedDict representing a domain object (both StarkNetDomain, StarknetDomain).
    """

    name: str
    version: str
    chainId: str
    revision: Optional[Revision]


class TypedDataDict(TypedDict):
    """
    TypedDict representing a TypedData object
    """

    types: Dict[str, List[ParameterDict]]
    primaryType: str
    domain: DomainDict
    message: Dict[str, Any]


class TypeContext(TypedDict):
    parent: str
    key: str
