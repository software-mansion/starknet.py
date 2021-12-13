from typing import Union, Dict

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


def is_felt_pointer(cairo_type: CairoType) -> bool:
    return isinstance(cairo_type, TypePointer) and isinstance(
        cairo_type.pointee, TypeFelt
    )


AddressRepresentation = Union[int, str]
Address = int


def parse_address(value: AddressRepresentation) -> Address:
    if isinstance(value, int):
        return value

    try:
        return int(value, 16)
    except TypeError as t_err:
        raise TypeError("Invalid address format.") from t_err


def net_address_from_net(net: str) -> str:
    return {
        "mainnet": "https://alpha-mainnet.starknet.io",
        "testnet": "https://alpha4.starknet.io",
    }.get(net, net)


InvokeFunction = IF
Deploy = D
Transaction = T
