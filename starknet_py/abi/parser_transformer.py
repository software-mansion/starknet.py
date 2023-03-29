import os

import lark
from lark import Transformer, v_args

from starknet_py.cairo.data_types import FeltType, Option


class ParserTransformer(Transformer):
    """
    Transforms the lark tree into an AST based on the classes defined in ast/*.py.
    """

    def __default__(self, data: str, children, meta):
        print(data, children, meta)
        raise TypeError(f"Unable to parse tree node of type {data}")

    @v_args(inline=True)
    def start(self, value):
        return value

    def type(self, value):
        return value[0]

    def type_felt(self, value):
        return FeltType()

    def type_uint(self, value):
        return FeltType()

    def type_unit(self, value):
        return None

    def type_option(self, value):
        return Option()

    def struct(self, value):
        name = ""
        for token in value:
            if isinstance(token, str):
                name += token
                name += "::"
        return name[:-2]


def parse(
    code: str,
):
    """
    Parses the given string and returns an AST tree based on the classes in ast/*.py.
    code_type is the ebnf rule to start from (e.g., 'expr' or 'cairo_file').
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
