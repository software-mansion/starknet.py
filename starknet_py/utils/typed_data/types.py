from typing import Optional, Union

from typing_extensions import TypedDict


class StarkNetDomain(TypedDict):
    name: Optional[str]
    version: Optional[str]
    chainId: Optional[Union[str, int]]


class TypedData:
    types: dict
    primary_type: str
    domain: StarkNetDomain
    message: dict

    def __init__(self, types, primary_type, domain, message):
        self.types = types
        self.primary_type = primary_type
        self.domain = domain
        self.message = message
