from math import log2
from typing import Any, List, Optional, Tuple, Union

import lark
from lark import Token, Transformer

from starknet_py.cairo.data_types import (
    ArrayType,
    BoolType,
    CairoType,
    FeltType,
    FixedSizeArrayType,
    NonZeroType,
    OptionType,
    TupleType,
    TypeIdentifier,
    UintType,
    UnitType,
)

ABI_EBNF = """
    IDENTIFIER: /[a-zA-Z_][a-zA-Z_0-9]*/
    
    type: "@"? actual_type
    
    actual_type: type_unit
        | type_bool
        | type_felt
        | type_bytes
        | type_uint
        | type_bounded_int
        | type_contract_address
        | type_class_hash
        | type_storage_address
        | type_option
        | type_non_zero
        | type_array
        | type_fixed_size_array
        | type_span
        | tuple
        | type_identifier
    
    
    type_unit: "()"
    type_felt: "core::felt252"
    type_bytes: "core::bytes_31::bytes31"
    type_bool: "core::bool"
    type_uint: "core::integer::u" INT
    type_bounded_int: "core::internal::BoundedInt::<" INT "," WS? INT ">" | "core::internal::bounded_int::BoundedInt::<" INT "," WS? INT ">"
    type_contract_address: "core::starknet::contract_address::ContractAddress"
    type_class_hash: "core::starknet::class_hash::ClassHash"
    type_storage_address: "core::starknet::storage_access::StorageAddress"
    type_option: "core::option::Option::<" (type | type_identifier) ">"
    type_array: "core::array::Array::<" (type | type_identifier) ">"
    type_fixed_size_array: "[" (type | type_identifier) ";" INT "]"
    type_span: "core::array::Span::<" (type | type_identifier) ">"
    type_non_zero: "core::zeroable::NonZero::<" (type | type_identifier) ">"
    
    tuple: "(" type? ("," type?)* ")"
    
    type_identifier: (IDENTIFIER | "::")+ ("<" (type | ",")+ ">")?
    
    
    %import common.INT
    %import common.WS
    %ignore WS
"""


class ParserTransformer(Transformer):
    """
    Transforms the lark tree into CairoTypes.
    """

    def __init__(self, type_identifiers: Optional[dict] = None) -> None:
        if type_identifiers is None:
            type_identifiers = {}
        self.type_identifiers = type_identifiers
        super(Transformer, self).__init__()

    # pylint: disable=no-self-use

    def __default__(self, data: str, children, meta):
        raise TypeError(f"Unable to parse tree node of type {data}.")

    def type(self, value: List[Optional[CairoType]]) -> Optional[CairoType]:
        """
        Tokens are read bottom-up, so here all of them are parsed and should be just returned.
        `Optional` is added in case of the unit type.
        """
        assert len(value) == 1
        return value[0]

    def actual_type(self, value) -> Optional[CairoType]:
        return value[0]

    def type_felt(self, _value: List[Any]) -> FeltType:
        """
        Felt does not contain any additional arguments, so `_value` is just an empty list.
        """
        return FeltType()

    def type_bytes(self, _value: List[Any]) -> FeltType:
        """
        Felt does not contain any additional arguments, so `_value` is just an empty list.
        """
        return FeltType()

    def type_bool(self, _value: List[Any]) -> BoolType:
        """
        Bool does not contain any additional arguments, so `_value` is just an empty list.
        """
        return BoolType()

    def type_uint(self, value: List[Token]) -> UintType:
        """
        Uint type contains information about its size. It is present in the value[0].
        """
        return UintType(int(value[0]))

    def type_bounded_int(self, value: List[Token]) -> UintType:
        """
        BoundedInt Uint type contains information about its ranges. They are present in the value[0] and value[2].
        """
        if value[0] != "0":
            raise ValueError("BoundedInt should start from 0.")

        bits = log2(int(value[2]) + 1)

        return UintType(int(bits))

    def type_unit(self, _value: List[Any]) -> UnitType:
        """
        `()` type.
        """
        return UnitType()

    def type_option(self, value: List[CairoType]) -> OptionType:
        """
        Option includes an information about which type it eventually represents.
        `Optional` is added in case of the unit type.
        """
        return OptionType(value[0])

    def type_array(self, value: List[CairoType]) -> ArrayType:
        """
        Array contains values of type under `value[0]`.
        """
        return ArrayType(value[0])

    def type_fixed_size_array(
        self, value: Tuple[CairoType, Token]
    ) -> FixedSizeArrayType:
        """
        Fixed-size array contains values of type under `value[0]`.
        """
        cairo_type, size_token = value
        size = int(size_token)

        return FixedSizeArrayType(cairo_type, size)

    def type_span(self, value: List[CairoType]) -> ArrayType:
        """
        Span contains values of type under `value[0]`.
        """
        return ArrayType(value[0])

    def type_identifier(self, tokens: List[Token]) -> TypeIdentifier:
        """
        Structs and enums are defined as follows: (IDENTIFIER | "::")+ [some not important info]
        where IDENTIFIER is a string.

        Tokens would contain strings and types (if it is present).
        We are interested only in the strings because a structure (or enum) name can be built from them.
        """
        name = "::".join(token for token in tokens if isinstance(token, str))
        if name in self.type_identifiers:
            return self.type_identifiers[name]
        return TypeIdentifier(name)

    def type_contract_address(self, _value: List[Any]) -> FeltType:
        """
        ContractAddress is represented by the felt252.
        """
        return FeltType()

    def type_class_hash(self, _value: List[Any]) -> FeltType:
        """
        ClassHash is represented by the felt252.
        """
        return FeltType()

    def type_storage_address(self, _value: List[Any]) -> FeltType:
        """
        StorageAddress is represented by the felt252.
        """
        return FeltType()

    def tuple(self, types: List[CairoType]) -> TupleType:
        """
        Tuple contains values defined in the `types` argument.
        """
        return TupleType(types)

    def type_non_zero(self, value: List[Union[FeltType, UintType]]) -> NonZeroType:
        """
        NonZero contains value which is never zero.
        """
        return NonZeroType(value[0])


def parse(
    code: str,
    type_identifiers,
) -> CairoType:
    """
    Parse the given string and return a CairoType.
    """
    grammar_parser = lark.Lark(
        grammar=ABI_EBNF,
        start="type",
        parser="earley",
    )
    parsed_lark_tree = grammar_parser.parse(code)

    parser_transformer = ParserTransformer(type_identifiers)
    cairo_type = parser_transformer.transform(parsed_lark_tree)

    return cairo_type
