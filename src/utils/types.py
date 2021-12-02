import sys
from typing import Union

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


if sys.version_info >= (3, 8):
    from typing import Literal

    NetType = Literal["mainnet", "testnet", "devnet"]
else:
    NetType = str


def net_address_from_type(net_type: NetType) -> str:
    if sys.version_info < (3, 8):
        assert net_type in ["mainnet", "testnet", "devnet"]

    return {
        "mainnet": "https://alpha-mainnet.starknet.io",
        "testnet": "https://alpha4.starknet.io",
        "devnet": "http://localhost:5000/",
    }[net_type]
