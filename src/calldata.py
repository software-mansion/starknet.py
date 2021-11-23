from dataclasses import dataclass
from typing import List

from starkware.cairo.lang.compiler.ast.cairo_types import (
    TypeFelt,
    TypePointer,
    CairoType,
    TypeStruct,
)
from starkware.cairo.lang.compiler.identifier_definition import (
    StructDefinition,
)
from starkware.cairo.lang.compiler.identifier_manager import (
    IdentifierManager,
)
from starkware.cairo.lang.compiler.parser import parse_type
from starkware.cairo.lang.compiler.type_system import mark_type_resolved
from starkware.cairo.lang.compiler.type_utils import check_felts_only_type

from .types import is_felt_pointer

ABIFunctionEntry = dict


@dataclass(frozen=True)
class CalldataTransformer:
    abi: ABIFunctionEntry
    identifier_manager: IdentifierManager

    def __call__(self, *args, **kwargs) -> List[int]:
        inputs = self.abi["inputs"]
        type_by_name = self._remove_array_lengths(
            {i["name"]: mark_type_resolved(parse_type(i["type"])) for i in inputs}
        )

        named_arguments = {**kwargs}
        # Assign args to named arguments
        assert len(args) <= len(
            type_by_name
        ), f"Provided {len(args)} positional arguments, {len(type_by_name)} possible"
        for arg, input_name in zip(args, type_by_name.keys()):
            assert (
                input_name not in named_arguments
            ), f"Both positional and named argument provided for {input_name}"
            named_arguments[input_name] = arg

        calldata: List[int] = []
        for name, type in type_by_name.items():
            assert name in named_arguments, f"Input {name} not provided"
            values = self._get_value(name, named_arguments[name], type)
            calldata.extend(values)

        return calldata

    def _remove_array_lengths(self, type_by_name: dict) -> dict:
        """
        If it is an array ignore array_len argument, we prepend length to felt* by default,
        so we can omit this input.
        """
        to_return = {}

        for name, cairo_type in type_by_name.items():
            if name.endswith("_len") and isinstance(cairo_type, TypeFelt):
                array_key = name[:-4]
                if array_key in type_by_name and is_felt_pointer(
                    type_by_name[array_key]
                ):
                    continue

            to_return[name] = cairo_type

        return to_return

    def _get_value(self, name: str, value: any, cairo_type: CairoType) -> List[int]:
        if isinstance(cairo_type, TypeFelt):
            return [self._get_int(name, value)]

        if isinstance(cairo_type, TypeStruct):
            return self._get_struct(name, value, cairo_type)

        typ_size = check_felts_only_type(
            cairo_type=cairo_type,
            identifier_manager=self.identifier_manager,
        )
        if typ_size is not None:
            return self._get_n_ints(name, typ_size, value)

        if cairo_type == TypePointer(pointee=TypeFelt()):
            values = self._get_ints(name, value)
            return [len(values), *values]

        raise Exception(f"Type {cairo_type} not supported")

    def _get_int(self, name: str, value: any) -> int:
        assert isinstance(value, int), f"{name} should be int"
        return value

    def _get_ints(self, name: str, values: any) -> List[int]:
        return [self._get_int(f"{name}[{i}]", value) for i, value in enumerate(values)]

    def _get_n_ints(self, name: str, n: int, values: any) -> List[int]:
        values = self._get_ints(name, values)

        assert n > 0, "Can't request less than 1 value"
        assert len(values) == n, f"Length of {name} is {len(values)}. Expected {n}."

        return values

    def _get_struct(self, name: str, value: any, type) -> List[int]:
        assert isinstance(value, dict), f"Expected {name} to be a dict"

        result = []

        definition = self.identifier_manager.get(
            type.resolved_scope
        ).identifier_definition
        assert isinstance(definition, StructDefinition), "Invalid definition found"

        for member_name, member in definition.members.items():
            assert member_name in value, f"{name}[{member_name}] not provided"
            values = self._get_value(
                f"{name}.{member_name}", value[member_name], member.cairo_type
            )
            result.extend(values)

        return result
