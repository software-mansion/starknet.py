from __future__ import annotations

from typing import Dict

from starknet_py.abi.v1.parser_transformer import parse
from starknet_py.cairo.data_types import CairoType, StructType


class UnknownCairoTypeError(ValueError):
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

        :param defined_types: dictionary containing all defined types. For now, they can only be structures.
        """
        self.defined_types = defined_types
        for name, struct in defined_types.items():
            if name != struct.name:
                raise ValueError(
                    f"Keys must match name of type, '{name}' != '{struct.name}'."
                )

    def parse_inline_type(self, type_string: str) -> CairoType:
        """
        Inline type is one that can be used inline, for instance as return type. For instance
        (a: Uint256, b: felt*, c: (felt, felt)). Structure can only be referenced in inline type, can't be defined
        this way.

        :param type_string: type to parse.
        """
        parsed = parse(type_string)

        if isinstance(parsed, str):
            return self._get_struct(parsed)
        return parsed

    def _get_struct(self, name: str):
        for struct_name in self.defined_types.keys():
            if name in struct_name:
                return self.defined_types[struct_name]
        raise UnknownCairoTypeError(name)
