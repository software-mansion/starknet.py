"""
TypedDict structures for TypedData
"""

from typing import Any, Dict, List, Optional, TypedDict

from starknet_py.net.schemas.common import Revision


class ParameterDict(TypedDict):
    """
    TypedDict representing a Parameter object
    """

    name: str
    type: str
    contains: Optional[str]


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
