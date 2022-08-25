from dataclasses import dataclass
from typing import Optional, Union

from starknet_py.utils.typing import TypedDict


class StarkNetDomain(TypedDict):
    name: Optional[str]
    version: Optional[str]
    chainId: Optional[Union[str, int]]


@dataclass(frozen=True)
class TypedData:
    types: dict
    primary_type: str
    domain: StarkNetDomain
    message: dict
