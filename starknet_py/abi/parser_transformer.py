import os
from collections.abc import Sequence
from typing import Optional

import lark
from lark import Transformer, v_args, UnexpectedToken, LarkError
from lark.exceptions import VisitError
from starkware.cairo.lang.compiler.ast.expr import ExprIdentifier
from starkware.cairo.lang.compiler.error_handling import InputFile, LocationError
from starkware.cairo.lang.compiler.parser import wrap_lark_error

from starknet_py.cairo.data_types import FeltType


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

    def struct(self, value):
        name = ""
        for token in value:
            try:
                if isinstance(token, str):
                    name += token
                    name += "::"
            except Exception:
                continue
        return name[:-2]


def parse(
    filename: Optional[str],
    code: str,
    code_type: str,
    expected_type,
):
    """
    Parses the given string and returns an AST tree based on the classes in ast/*.py.
    code_type is the ebnf rule to start from (e.g., 'expr' or 'cairo_file').
    """
    grammar_parser = lark.Lark(
        grammar=open(os.path.join(os.path.dirname(__file__), "abi.ebnf"), "r").read(),
        start="start",
        parser="lalr",
    )

    parsed = grammar_parser.parse(code)

    transformed = ParserTransformer().transform(parsed)

    return transformed
