"""
TypedDict structures for TypedData
"""

from typing import Any, Dict, List, TypedDict, Union


class Parameter(TypedDict):
    """
    TypedDict representing a Parameter object
    """

    name: str
    type: str


class StarkNetDomain(TypedDict):
    """
    TypedDict representing a StarkNetDomain object
    """

    name: str
    version: str
    chainId: Union[str, int]


class TypedData(TypedDict):
    """
    TypedDict representing a TypedData object
    """

    types: Dict[str, List[Parameter]]
    primaryType: str
    domain: StarkNetDomain
    message: Dict[str, Any]
