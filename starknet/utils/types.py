from typing import Union

from starkware.cairo.lang.compiler.ast.cairo_types import (
    CairoType,
    TypePointer,
    TypeFelt,
)
from starkware.cairo.lang.compiler.identifier_definition import StructDefinition
from starkware.crypto.signature.signature import FIELD_PRIME
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


MIN_FELT = -FIELD_PRIME / 2
MAX_FELT = FIELD_PRIME / 2


def cairo_vm_range_check(value: int):
    if not 0 <= value < FIELD_PRIME:
        raise ValueError(
            f"Felt is expected to be in range [0; {FIELD_PRIME}), got {value}"
        )


def felt_to_int(value: int):
    """
    :param value: Felt output from cairo-vm
    :return: corresponding python value, assuming viable (-P/2; P/2) range
    """
    cairo_vm_range_check(value)
    return -FIELD_PRIME + value if value * 2 > FIELD_PRIME else value


def int_to_felt(value: int):
    """
    :param value: Integer value in python
    :return: Corresponding cairo-vm compatible value in range [0; P)
    :raises: ``ValueError`` if provided value is not cairo-vm compatible
            (namely, ranging (-P/2; P/2), P being base prime in cairo)
    """
    if not -FIELD_PRIME < 2 * value < FIELD_PRIME:
        raise ValueError(
            f"Int input is expected to be in range (-{FIELD_PRIME/2}; {FIELD_PRIME/2})), got {value}"
        )
    output = FIELD_PRIME + value if value < 0 else value
    cairo_vm_range_check(output)
    return output
