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
        raise ValueError('Invalid address format.')
