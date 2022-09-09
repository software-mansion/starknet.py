"""
TypedDict structures for TypedData
"""

from typing import Dict, Union, TypedDict, Any


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

    types: Dict[str, Any]
    primary_type: str
    domain: StarkNetDomain
    message: dict
