from typing import Union

from starkware.cairo.lang.compiler.ast.cairo_types import (
    CairoType,
    TypePointer,
    TypeFelt,
)
from starkware.starknet.services.api.gateway.transaction import (
    InvokeFunction as IF,
    Deploy as D,
    Transaction as T,
)


def is_felt_pointer(type: CairoType) -> bool:
    return isinstance(type, TypePointer) and isinstance(type.pointee, TypeFelt)


AddressRepresentation = Union[int, str]
Address = int


def parse_address(value: AddressRepresentation) -> Address:
    if isinstance(value, int):
        return value

    try:
        return int(value, 16)
    except ValueError:
        raise ValueError("Invalid address format.")


def net_address_from_net(net: str) -> str:
    nets = {
        "mainnet": "https://alpha-mainnet.starknet.io",
        "testnet": "https://alpha4.starknet.io",
    }
    predefined_net_addr = nets.get(net)
    return predefined_net_addr if predefined_net_addr else net


InvokeFunction = IF
Deploy = D
Transaction = T
