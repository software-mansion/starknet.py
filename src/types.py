from starkware.cairo.lang.compiler.ast.cairo_types import (
    CairoType,
    TypePointer,
    TypeFelt,
)


def is_felt_pointer(type: CairoType) -> bool:
    return isinstance(type, TypePointer) and isinstance(type.pointee, TypeFelt)
