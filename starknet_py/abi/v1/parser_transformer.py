import os

import lark
from lark import Transformer, v_args

from starknet_py.cairo.data_types import (
    ArrayType,
    CairoType,
    FeltType,
    Option,
    TupleType,
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
    def start(self, value):
        return value

    def type(self, value):
        return value[0]

    def type_felt(self, _value):
        return FeltType()

    def type_uint(self, value):
        return UintType(int(value[0]))

    def type_unit(self, _value):
        return None

    def type_option(self, _value):
        return Option(_value[0])

    def type_array(self, value):
        return ArrayType(value[0])

    def struct(self, tokens):
        return "::".join(token for token in tokens if isinstance(token, str))

    def type_address(self, _value):
        return FeltType()

    def tuple(self, types):
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
