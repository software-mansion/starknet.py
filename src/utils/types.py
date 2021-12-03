import enum
from typing import Union, NewType

from starkware.cairo.lang.compiler.ast.cairo_types import (
    CairoType,
    TypePointer,
    TypeFelt,
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


class NetAddress(enum.Enum):
    mainnet = "https://alpha-mainnet.starknet.io"
    testnet = "https://alpha4.starknet.io"


Net = NewType("Net", Union[NetAddress, str])


def net_address_from_net(net: Net) -> str:
    if isinstance(net, NetAddress):
        net = net.value
    return net
