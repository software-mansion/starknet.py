import os

import lark

from starknet_py.cairo.deprecated_parse.parser_transformer import ParserTransformer


def parse(code: str):
    """
    Parses the given string and returns an AST tree based on the classes in ast/*.py.
    code_type is the ebnf rule to start from (e.g., 'expr' or 'cairo_file').
    """
    with open(
        os.path.join(os.path.dirname(__file__), "cairo.ebnf"), "r", encoding="utf-8"
    ) as grammar_file:
        grammar = grammar_file.read()

    grammar_parser = lark.Lark(
        grammar=grammar,
        start=[
            "type",
        ],
        parser="lalr",
    )

    parsed = grammar_parser.parse(code)
    transformed = ParserTransformer().transform(parsed)

    return transformed
