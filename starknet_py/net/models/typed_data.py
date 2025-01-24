"""
TypedDict structures for TypedData
"""

import sys
from typing import Any, Dict, List, Optional, TypedDict

from starknet_py.net.schemas.common import Revision

if sys.version_info < (3, 11):
    from typing_extensions import NotRequired
else:
    from typing import NotRequired


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
