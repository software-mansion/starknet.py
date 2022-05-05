from dataclasses import dataclass
from typing import List, Callable, TypeVar, Generic, Tuple, Dict, NamedTuple
import itertools

from starkware.cairo.lang.compiler.ast.cairo_types import (
    TypeFelt,
    TypePointer,
    CairoType,
    TypeStruct,
    TypeTuple,
)
from starkware.cairo.lang.compiler.identifier_definition import (
    StructDefinition,
)
from starkware.cairo.lang.compiler.identifier_manager import (
    IdentifierManager,
)
from starkware.cairo.lang.compiler.parser import parse_type
from starkware.cairo.lang.compiler.type_system import mark_type_resolved

from starknet_py.cairo.felt import (
    is_uint256,
    uint256_range_check,
    cairo_vm_range_check,
    encode_shortstring,
)

ABIFunctionEntry = dict
CairoData = List[int]


def read_from_cairo_data(
    name: str, values: CairoData, n: int
) -> (CairoData, CairoData):
    if len(values) < n:
        raise ValueError(
            f"Output {name} expected {n} values, {len(values)} values are available."
        )

    return values[:n], values[n:]


# pylint: disable=invalid-name
UsedCairoType = TypeVar("UsedCairoType", bound=CairoType)

PythonType = TypeVar("PythonType")


@dataclass
class TypeTransformer(Generic[UsedCairoType, PythonType]):
    identifier_manager: IdentifierManager
    resolve_type: Callable[[CairoType], "TypeTransformer"]

    def from_python(
        self, cairo_type: UsedCairoType, name: str, value: any
    ) -> CairoData:
        raise NotImplementedError()

    def to_python(
        self, cairo_type: UsedCairoType, name: str, values: CairoData
    ) -> Tuple[PythonType, CairoData]:
        raise NotImplementedError()


class FeltTransformer(TypeTransformer[TypeFelt, int]):
    def from_python(self, cairo_type, name, value):
        if isinstance(value, str):
            value = encode_shortstring(value)
            return [value]

        if not isinstance(value, int):
            raise TypeError(f"{name} should be int.")
        cairo_vm_range_check(value)
        return [value]

    def to_python(self, cairo_type, name, values):
        [val], rest = read_from_cairo_data(name, values, 1)
        return val, rest


class StructTransformer(TypeTransformer[TypeStruct, dict]):
    def _definition(self, cairo_type: TypeStruct) -> StructDefinition:
        definition = self.identifier_manager.get(
            cairo_type.resolved_scope
        ).identifier_definition

        if not isinstance(definition, StructDefinition):
            raise ValueError(
                f"Invalid definition found for {cairo_type.resolved_scope}."
            )

        return definition

    def from_python(self, cairo_type, name, value):
        definition = self._definition(cairo_type)

        if is_uint256(definition) and isinstance(value, int):
            uint256_range_check(value)
            return [value & ((1 << 128) - 1), value >> 128]

        if not isinstance(value, dict):
            raise TypeError(f"Expected {name} to be a dict.")

        result = []
        for member_name, member in definition.members.items():
            if member_name not in value:
                raise ValueError(f"{name}[{member_name}] not provided.")

            values = self.resolve_type(member.cairo_type).from_python(
                member.cairo_type, f"{name}.{member_name}", value[member_name]
            )
            result.extend(values)

        return result

    def to_python(self, cairo_type, name, values) -> (dict, CairoData):
        definition = self._definition(cairo_type)
        if is_uint256(definition):
            low, high, *values = values
            value = (high << 128) + low
            uint256_range_check(value)
            return value, values

        result = {}
        for member_name, member in definition.members.items():
            transformed, values = self.resolve_type(member.cairo_type).to_python(
                member.cairo_type, f"{name}.{member_name}", values
            )
            result[member_name] = transformed

        return result, values


class TupleTransformer(TypeTransformer[TypeTuple, tuple]):
    def from_python(self, cairo_type, name, value):
        if len(value) != len(cairo_type.members):
            raise ValueError(
                f"Input {name} length mismatch: {len(value)} != {len(cairo_type.members)}."
            )

        if not cairo_type.is_named:
            return self._from_python_unnamed(cairo_type, name, value)
        return self._from_python_named(cairo_type, name, value)

    def _from_python_unnamed(self, cairo_type, name, value):
        values = [*value]

        results = []
        for index, member, member_type in zip(
            range(len(values)), values, cairo_type.members
        ):
            result = self.resolve_type(member_type).from_python(
                member_type, f"{name}[{index}]", member
            )
            results.extend(result)

        return results

    def _from_python_named(self, cairo_type, name, values):
        if not isinstance(values, dict) and not TupleTransformer.isnamedtuple(values):
            raise ValueError(
                f"Input {name} is a named tuple and must be dict or NamedTuple"
            )

        results = []

        if TupleTransformer.isnamedtuple(values):
            values = values._asdict()

        for member in cairo_type.members:
            result = self.resolve_type(member).from_python(
                member, f"{name}[{member.name}]", values[member.name]
            )
            results.extend(result)

        return results

    @staticmethod
    def isnamedtuple(value):
        return isinstance(value, tuple) and hasattr(value, "_fields")

    def to_python(self, cairo_type, name, values):
        if not cairo_type.is_named:
            return self._to_python_unnamed(cairo_type, name, values)
        return self._to_python_named(cairo_type, name, values)

    def _to_python_unnamed(self, cairo_type, name, values):
        result = []
        for index, member_type in enumerate(cairo_type.members):
            (name, transformed), values = self.resolve_type(member_type).to_python(
                member_type, f"{name}[{index}]", values
            )
            result.append(transformed)

        return (*result,), values

    def _to_python_named(self, cairo_type, name, values):
        result = {}
        for index, member_type in enumerate(cairo_type.members):
            (name, transformed), values = self.resolve_type(member_type).to_python(
                member_type, f"{name}[{index}]", values
            )
            result[name] = transformed

        res = NamedTuple(
            "Result", [(key, type(value)) for key, value in result.items()]
        )
        # pylint: disable=not-callable
        return res(**result), values


class TupleItemTransformer(TypeTransformer[TypeTuple.Item, tuple]):
    def from_python(self, cairo_type: UsedCairoType, name: str, value: any):
        value = self.resolve_type(cairo_type.typ).from_python(
            cairo_type.typ,
            cairo_type.name or "",
            value,
        )
        return value

    def to_python(self, cairo_type: UsedCairoType, name: str, values: CairoData):
        name = cairo_type.name or ""
        result, values = self.resolve_type(cairo_type.typ).to_python(
            cairo_type.typ, name, values
        )
        return (name, result), values


class ArrayTransformer(TypeTransformer[TypePointer, List[int]]):
    def from_python(self, cairo_type, name, value):
        inner_type = cairo_type.pointee

        transformer = self.resolve_type(inner_type)
        transformed = [
            transformer.from_python(inner_type, f"{name}[{i}]", value)
            for i, value in enumerate(value)
        ]
        array_len = len(transformed)
        array_data = list(itertools.chain(*transformed))
        return [array_len, *array_data]

    def to_python(self, cairo_type, name, values):
        [length], values = read_from_cairo_data(name, values, 1)
        inner_type = cairo_type.pointee
        transformer = self.resolve_type(inner_type)

        array = []
        rest = values
        for i in range(length):
            elem, rest = transformer.to_python(inner_type, f"{name}[{i}]", rest)
            array.append(elem)

        return array, rest


mapping = {
    TypeFelt: FeltTransformer,
    TypeTuple: TupleTransformer,
    TypeTuple.Item: TupleItemTransformer,
    TypePointer: ArrayTransformer,
    TypeStruct: StructTransformer,
}


@dataclass(frozen=True)
class DataTransformer:
    """
    Transforms data from python to Cairo format and back.
    """

    abi: ABIFunctionEntry
    identifier_manager: IdentifierManager

    def resolve_type(self, cairo_type: CairoType) -> TypeTransformer:
        return mapping[cairo_type.__class__](
            identifier_manager=self.identifier_manager,
            resolve_type=self.resolve_type,
        )

    def from_python(self, *args, **kwargs) -> (List[int], Dict[str, List[int]]):
        """
        Transforms params into Cairo representation.
        :return: tuple (full calldata, dict with all arguments with their Cairo representation)
        """
        type_by_name = self._abi_to_types(self.abi["inputs"])

        named_arguments = {**kwargs}

        if len(args) > len(type_by_name):
            raise TypeError(
                f"Provided {len(args)} positional arguments, {len(type_by_name)} possible."
            )

        # Assign args to named arguments
        for arg, input_name in zip(args, type_by_name.keys()):
            if input_name in named_arguments:
                raise TypeError(
                    f"Both positional and named argument provided for {input_name}."
                )
            named_arguments[input_name] = arg

        all_params: Dict[str, List[int]] = {}
        calldata: List[int] = []
        for name, cairo_type in type_by_name.items():
            if name not in named_arguments:
                raise TypeError(f"Input {name} not provided.")

            values = self.resolve_type(cairo_type).from_python(
                cairo_type, name, named_arguments[name]
            )

            all_params[name] = values

            calldata.extend(values)

        return calldata, all_params

    def to_python(self, values: CairoData) -> NamedTuple:
        type_by_name = self._abi_to_types(self.abi["outputs"])

        result = {}
        for name, cairo_type in type_by_name.items():
            transformed, values = self.resolve_type(cairo_type).to_python(
                cairo_type, name, values
            )
            result[name] = transformed

        result_tuple = NamedTuple(
            "Result", [(key, type(value)) for key, value in result.items()]
        )
        # pylint: disable=not-callable
        return result_tuple(**result)

    def _abi_to_types(self, abi_list) -> dict:
        return self._remove_array_lengths(
            {
                entry["name"]: mark_type_resolved(parse_type(entry["type"]))
                for entry in abi_list
            }
        )

    @staticmethod
    def _remove_array_lengths(type_by_name: dict) -> dict:
        """
        If it is an array ignore array_len argument, we prepend length to <type>* by default,
        so we can omit this input.
        """

        is_array_len = (
            lambda name, cairo_type: name.endswith("_len")
            and isinstance(cairo_type, TypeFelt)
            and name[:-4] in type_by_name
            and isinstance(type_by_name[name[:-4]], TypePointer)
        )

        return {k: v for k, v in type_by_name.items() if not is_array_len(k, v)}
