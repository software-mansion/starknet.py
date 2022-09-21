"""
TypedDict structures for TypedData
"""

from typing import Dict, Union, TypedDict, Any, List, Optional

from starknet_py.net.client_models import Hash


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


class DeployerConfigRequiredArgs(TypedDict):
    """
    TypedDict representing a UDC required arguments
    """

    class_hash: Hash


class DeployerConfig(DeployerConfigRequiredArgs, total=False):
    """
    TypedDict representing a UDC arguments
    """

    salt: Optional[int]
    unique: Optional[bool]
    constructor_calldata: Optional[Union[List[any], dict]]
