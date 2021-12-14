from typing import Union, Dict

from starkware.cairo.lang.compiler.ast.cairo_types import (
    CairoType,
    TypePointer,
    TypeFelt,
)
from starkware.cairo.lang.compiler.identifier_definition import StructDefinition
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
    except ValueError as v_err:
        raise ValueError("Invalid address format.") from v_err


def net_address_from_net(net: str) -> str:
    return {
        "mainnet": "https://alpha-mainnet.starknet.io",
        "testnet": "https://alpha4.starknet.io",
    }.get(net, net)


InvokeFunction = IF
Deploy = D
Transaction = T


class KeyedTuple(tuple):
    """
    Tuple with dictionary-like access.
    """

    # pylint: disable=super-init-not-called
    def __init__(self, properties: Dict[str, any]):
        for key in properties.keys():
            if not isinstance(key, str):
                raise ValueError("Only string keys are allowed in KeyedTuple.")

        self._properties = properties

    def __new__(cls, properties: Dict[str, any]):
        return super().__new__(cls, (prop for prop in properties.values()))

    def as_dict(self) -> dict:
        """
        Returns a regular dict representation.
        """
        return self._properties

    def __getitem__(self, item):
        if isinstance(item, int):
            return super().__getitem__(item)

        return self._properties[item]


def is_uint256(definition: StructDefinition) -> bool:
    (struct_name, *_) = definition.full_name.path

    return (
        struct_name == "Uint256"
        and len(definition.members.items()) == 2
        and definition.members.get("low")
        and definition.members.get("high")
        and isinstance(definition.members["low"].cairo_type, TypeFelt)
        and isinstance(definition.members["high"].cairo_type, TypeFelt)
    )


MAX_UINT256 = (1 << 256) - 1
MIN_UINT256 = 0


def uint256_range_check(value: int):
    if not MIN_UINT256 <= value <= MAX_UINT256:
        raise ValueError(f"UInt256 is expected to be in range [0;2^256), got {value}")
