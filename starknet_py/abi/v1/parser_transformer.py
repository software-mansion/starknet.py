import os
from typing import Any, List, Optional

import lark
from lark import Token, Transformer, v_args

from starknet_py.cairo.data_types import (
    ArrayType,
    CairoType,
    FeltType,
    OptionType,
    TupleType,
    TypeIdentifier,
    UintType,
)


class ParserTransformer(Transformer):
    """
    Transforms the lark tree into CairoTypes.
    """

    # pylint: disable=no-self-use

    def __default__(self, data: str, children, meta):
        raise TypeError(f"Unable to parse tree node of type {data}")

    @v_args(inline=True)
    def start(self, value) -> Optional[CairoType]:
        """
        Method all the entries starts from.
        """
        return value

    def type(self, value: List[Optional[CairoType]]) -> Optional[CairoType]:
        """
        Types starting with "core" or unit type "()".

        Tokens are read bottom-up, so here all of them are parsed and should be just returned.
        `Optional` is added in case of the unit type.
        """
        assert len(value) == 1
        return value[0]

    def type_felt(self, _value: List[Any]) -> FeltType:
        """
        Felt does not contain any additional arguments, so `_value` is just an empty list.
        """
        return FeltType()

    def type_uint(self, value: List[Token]) -> UintType:
        """
        Uint type contains information about it's size. It is present in the value[0].
        """
        return UintType(int(value[0]))

    def type_unit(self, _value: List[Any]) -> None:
        """
        () type.
        """
        return None

    def type_option(self, value: List[Optional[CairoType]]) -> OptionType:
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

    def struct(self, tokens: List[Token]) -> TypeIdentifier:
        """
        Structs are defined as follows: (IDENTIFIER | "::")+ ("<" type ">")*
        where IDENTIFIER is some string.

        Tokens would contain strings and type (if it is present).
        We are interested only in the strings because a structure name can be built from them.
        """
        name = "::".join(token for token in tokens if isinstance(token, str))
        return TypeIdentifier(name)

    def type_address(self, _value: List[Any]) -> FeltType:
        """
        ContractAddress is represented by the felt252.
        """
        return FeltType()

    def tuple(self, types: List[CairoType]) -> TupleType:
        """
        Tuple contains values defined in the `types` argument.
        """
        return TupleType(types)


def parse(
    code: str,
) -> CairoType:
    """
    Parse the given string and return a CairoType.
    """
    with open(
        os.path.join(os.path.dirname(__file__), "abi.ebnf"), "r", encoding="utf-8"
    ) as grammar_file:
        grammar = grammar_file.read()

    grammar_parser = lark.Lark(
        grammar=grammar,
        start="start",
        parser="lalr",
    )
    parsed = grammar_parser.parse(code)

    transformed = ParserTransformer().transform(parsed)

    return transformed
