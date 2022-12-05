from __future__ import annotations
from collections import OrderedDict
from typing import Dict

from starkware.cairo.lang.compiler.parser import parse_type
import starkware.cairo.lang.compiler.ast.cairo_types as cairo_lang_types

from starknet_py.cairo.data_types import (
    CairoType,
    FeltType,
    TupleType,
    NamedTupleType,
    ArrayType,
    StructType,
)


class UnknownTypeError(ValueError):
    """
    Error thrown when TypeParser finds type that was not declared prior to parsing.
    """

    type_name: str

    def __init__(self, type_name: str):
        super().__init__(f"Type '{type_name}' is not defined")
        self.type_name = type_name


class TypeParser:
    """
    Low level utility class for parsing Cairo types that can be used in external methods.
    """

    defined_types: Dict[str, StructType]

    def __init__(self, defined_types: Dict[str, StructType]):
        """
        TypeParser constructor.

        :param defined_types: dictionary containing all defined types. For now they can only be structures.
        """
        self.defined_types = defined_types
        for name, struct in defined_types.items():
            if name != struct.name:
                raise ValueError(
                    f"Keys must match name of type, [{name}] != [{struct.name}]"
                )

    def parse_inline_type(self, type_string: str) -> CairoType:
        """
        Inline type it one that can be used inline. For instance (a: Uint256, b: felt*, c: (felt, felt)).

        :param type_string: type to parse
        """
        parsed = parse_type(type_string)
        return self._transform_cairo_lang_type(parsed)

    def _transform_cairo_lang_type(
        self, cairo_type: cairo_lang_types.CairoType
    ) -> CairoType:
        if isinstance(cairo_type, cairo_lang_types.TypeFelt):
            return FeltType()

        if isinstance(cairo_type, cairo_lang_types.TypePointer):
            return ArrayType(self._transform_cairo_lang_type(cairo_type.pointee))

        if isinstance(cairo_type, cairo_lang_types.TypeIdentifier):
            return self._get_struct(str(cairo_type.name))

        if isinstance(cairo_type, cairo_lang_types.TypeTuple):
            # Cairo returns is_named when there are no members
            if cairo_type.is_named and len(cairo_type.members) != 0:
                return NamedTupleType(
                    OrderedDict(
                        (member.name, self._transform_cairo_lang_type(member.typ))
                        for member in cairo_type.members
                    )
                )

            return TupleType(
                [
                    self._transform_cairo_lang_type(member.typ)
                    for member in cairo_type.members
                ]
            )

        # Contracts don't support codeoffset as input/output type, user can only use it if it was defined in types
        if isinstance(cairo_type, cairo_lang_types.TypeCodeoffset):
            return self._get_struct("codeoffset")

        # Other options are: TypeFunction, TypeStruct
        # Neither of them are possible. In particular TypeStruct is not possible because we parse structs without
        # info about other structs, so they will be just TypeIdentifier (structure that was not parsed).

        # This is an error of our logic, so we throw a RuntimeError.
        raise RuntimeError(f"Received unknown type [{cairo_type}] from parser")

    def _get_struct(self, name: str):
        if name not in self.defined_types:
            raise UnknownTypeError(name)
        return self.defined_types[name]
