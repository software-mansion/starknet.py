import warnings
from dataclasses import dataclass
from typing import (
    List,
    Callable,
    TypeVar,
    Generic,
    Tuple,
    Dict,
    NamedTuple,
    Any,
    cast,
    Union,
)
from collections import namedtuple
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
from starknet_py.utils.data_transformer.errors import (
    InvalidValueException,
    InvalidTypeException,
)

ABIFunctionEntry = Dict
CairoData = List[int]


class Result:
    def __init__(self, tuple_value: NamedTuple, name_mapping: Dict, dict_value: Dict):
        self.tuple_value = tuple_value
        self.name_mapping = name_mapping
        self.dict_value = dict_value

    def __eq__(self, other):
        return self.tuple_value == other

    def __getattr__(self, item):
        return getattr(self.tuple_value, self.name_mapping[item])

    def __getitem__(self, item):
        return self.tuple_value[item]

    def __iter__(self):
        return self.tuple_value.__iter__()

    def __str__(self):
        result = ", ".join(
            f"{name}={getattr(self.tuple_value, key)}"
            for name, key in self.name_mapping.items()
        )
        return f"Result({result})"

    def __repr__(self):
        return self.__str__()

    def _asdict(self):
        return self.dict_value


def construct_result_object(result: dict) -> NamedTuple:
    fields = result.keys()
    named_tuple_class = namedtuple(
        field_names=fields,
        typename="Result",
        rename=True,
    )
    # pylint: disable=protected-access
    name_mapping = dict(zip(fields, named_tuple_class._fields))
    dict_value = {name_mapping[key]: value for key, value in result.items()}
    tuple_value = named_tuple_class(**dict_value)

    return cast(
        NamedTuple,
        Result(
            tuple_value=tuple_value, name_mapping=name_mapping, dict_value=dict_value
        ),
    )  # We pretend Result is a named tuple


def read_from_cairo_data(
    name: str, values: CairoData, n: int
) -> Tuple[CairoData, CairoData]:
    if len(values) < n:
        raise InvalidValueException(
            f"Output {name} expected {n} values, {len(values)} values are available."
        )

    return values[:n], values[n:]


# pylint: disable=invalid-name
UsedCairoType = TypeVar("UsedCairoType", bound=CairoType)

PythonType = TypeVar("PythonType")

RemainingFelts = CairoData
T = TypeVar("T")
PythonResult = Tuple[T, RemainingFelts]


@dataclass
class TypeTransformer(Generic[UsedCairoType, PythonType]):
    identifier_manager: IdentifierManager
    resolve_type: Callable[[CairoType], "TypeTransformer"]

    def from_python(
        self, cairo_type: UsedCairoType, name: str, value: Any
    ) -> CairoData:
        raise NotImplementedError()

    def to_python(
        self, cairo_type: UsedCairoType, name: str, values: CairoData
    ) -> PythonResult[PythonType]:
        raise NotImplementedError()


class FeltTransformer(TypeTransformer[TypeFelt, int]):
    def from_python(self, cairo_type, name, value) -> CairoData:
        if isinstance(value, str):
            value = encode_shortstring(value)
            return [value]

        if not isinstance(value, int):
            raise InvalidTypeException(f"{name} should be int.")
        cairo_vm_range_check(value)
        return [value]

    def to_python(self, cairo_type, name, values) -> PythonResult[int]:
        [val], rest = read_from_cairo_data(name, values, 1)
        cairo_vm_range_check(val)
        return cast(int, val), rest


# Uint256 are structs as well, we return them as integers
StructTransformerResult = Union[Dict, int]


class StructTransformer(TypeTransformer[TypeStruct, StructTransformerResult]):
    def _definition(self, cairo_type: TypeStruct) -> StructDefinition:
        definition = self.identifier_manager.get(cairo_type.scope).identifier_definition

        if not isinstance(definition, StructDefinition):
            raise InvalidValueException(
                f"Invalid definition found for {cairo_type.scope}."
            )

        return definition

    def from_python(self, cairo_type, name, value) -> CairoData:
        definition = self._definition(cairo_type)

        if is_uint256(definition) and isinstance(value, int):
            uint256_range_check(value)
            return [value & ((1 << 128) - 1), value >> 128]

        if not isinstance(value, dict):
            raise InvalidTypeException(f"Expected {name} to be a dict.")

        result = []
        for member_name, member in definition.members.items():
            if member_name not in value:
                raise InvalidValueException(f"{name}[{member_name}] not provided.")

            values = self.resolve_type(member.cairo_type).from_python(
                member.cairo_type, f"{name}.{member_name}", value[member_name]
            )
            result.extend(values)

        return result

    def to_python(
        self, cairo_type, name, values
    ) -> PythonResult[StructTransformerResult]:
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


class TupleTransformer(TypeTransformer[TypeTuple, Tuple]):
    def from_python(self, cairo_type, name, value) -> CairoData:
        if len(value) != len(cairo_type.members):
            raise InvalidValueException(
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
            raise InvalidValueException(
                f"Input {name} is a named tuple and must be dict or NamedTuple"
            )

        results = []

        if TupleTransformer.isnamedtuple(values):
            # noinspection PyUnresolvedReferences, PyProtectedMember
            values = values._asdict()  # pyright: ignore

        for member in cairo_type.members:
            result = self.resolve_type(member).from_python(
                member, f"{name}[{member.name}]", values[member.name]
            )
            results.extend(result)

        return results

    @staticmethod
    def isnamedtuple(value) -> bool:
        return isinstance(value, tuple) and hasattr(value, "_fields")

    def to_python(self, cairo_type, name, values) -> PythonResult[Tuple]:
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

        res = construct_result_object(result)
        return res, values


class TupleItemTransformer(TypeTransformer[TypeTuple.Item, Any]):
    def from_python(
        self, cairo_type: TypeTuple.Item, name: str, value: Any
    ) -> CairoData:
        value = self.resolve_type(cairo_type.typ).from_python(
            cairo_type.typ,
            cairo_type.name or "",
            value,
        )
        return value

    def to_python(
        self, cairo_type: TypeTuple.Item, name: str, values: CairoData
    ) -> PythonResult[Any]:
        name = cairo_type.name or ""
        result, values = self.resolve_type(cairo_type.typ).to_python(
            cairo_type.typ, name, values
        )
        return (name, result), values


class ArrayTransformer(TypeTransformer[TypePointer, List[int]]):
    def from_python(self, cairo_type, name, value) -> CairoData:
        inner_type = cairo_type.pointee

        transformer = self.resolve_type(inner_type)
        transformed = [
            transformer.from_python(inner_type, f"{name}[{i}]", value)
            for i, value in enumerate(value)
        ]
        array_len = len(transformed)
        array_data = list(itertools.chain(*transformed))
        return [array_len, *array_data]

    def to_python(self, cairo_type, name, values) -> PythonResult[List[int]]:
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
class CairoSerializer:
    """
    Transforms data from python to Cairo format and back.
    """

    identifier_manager: IdentifierManager

    def resolve_type(self, cairo_type: CairoType) -> TypeTransformer:
        # noinspection PyTypeChecker
        return mapping[cairo_type.__class__](
            identifier_manager=self.identifier_manager,
            resolve_type=self.resolve_type,
        )

    def from_python(
        self, value_types: List[dict], *args, **kwargs
    ) -> Tuple[List[int], Dict[str, List[int]]]:
        """
        Transforms params into Cairo representation.

        :param value_types: Types of values to be serialized
        :return: tuple (full calldata, dict with all arguments with their Cairo representation)
        :raises InvalidValueException: when an error occurred while transforming a value
        :raises InvalidTypeException: when wrong type was provided
        """
        type_by_name = self._abi_to_types(value_types)

        named_arguments = {**kwargs}

        if len(args) > len(type_by_name):
            raise InvalidTypeException(
                f"Provided {len(args)} positional arguments, {len(type_by_name)} possible."
            )

        key_diff = set(named_arguments.keys()).difference(set(type_by_name))

        if key_diff:
            raise InvalidTypeException(
                f"Unnecessary named arguments provided: {key_diff}."
            )

        # Assign args to named arguments
        for arg, input_name in zip(args, type_by_name.keys()):
            if input_name in named_arguments:
                raise InvalidTypeException(
                    f"Both positional and named argument provided for {input_name}."
                )
            named_arguments[input_name] = arg

        all_params: Dict[str, List[int]] = {}
        calldata: List[int] = []
        for name, cairo_type in type_by_name.items():
            if name not in named_arguments:
                raise InvalidTypeException(f"Input {name} not provided.")

            try:
                values = self.resolve_type(cairo_type).from_python(
                    cairo_type, name, named_arguments[name]
                )
            except ValueError as err:
                raise InvalidValueException(str(err)) from err
            except TypeError as err:
                raise InvalidTypeException(str(err)) from err

            all_params[name] = values

            calldata.extend(values)

        return calldata, all_params

    def to_python(self, value_types: List[dict], values: CairoData) -> NamedTuple:
        """
        Transforms params into Python representation.

        :param value_types: Types of values to be serialized
        :param values: Values to be serialized
        :return: tuple (full calldata, dict with all arguments with their Cairo representation)
        :raises InvalidValueException: when an error occurred while transforming a value
        :raises InvalidTypeException: when wrong type was provided
        """
        type_by_name = self._abi_to_types(value_types)
        initial_len = len(values)

        result = {}
        for name, cairo_type in type_by_name.items():
            try:
                transformed, values = self.resolve_type(cairo_type).to_python(
                    cairo_type, name, values
                )
            except ValueError as err:
                raise InvalidValueException(str(err)) from err
            except TypeError as err:
                raise InvalidTypeException(str(err)) from err

            result[name] = transformed

        if len(values) > 0:
            raise InvalidValueException(
                f"Too many values provided, expected {initial_len - len(values)} got {initial_len}."
            )

        return construct_result_object(result)

    def _abi_to_types(self, abi_list) -> dict:
        return self._remove_array_lengths(
            {
                entry["name"]: mark_type_resolved(parse_type(entry["type"]))
                for entry in abi_list
            }
        )

    @staticmethod
    def _is_array_len(name, cairo_type, type_by_name: dict) -> bool:
        return (
            name.endswith("_len")
            and isinstance(cairo_type, TypeFelt)
            and name[:-4] in type_by_name
            and isinstance(type_by_name[name[:-4]], TypePointer)
        )

    @staticmethod
    def _remove_array_lengths(type_by_name: dict) -> dict:
        """
        If it is an array ignore array_len argument, we prepend length to <type>* by default,
        so we can omit this input.
        """
        return {
            k: v
            for k, v in type_by_name.items()
            if not CairoSerializer._is_array_len(k, v, type_by_name=type_by_name)
        }


class FunctionCallSerializer:
    """
    Transforms function call data from python to Cairo format and back.
    """

    def __init__(self, abi: ABIFunctionEntry, identifier_manager: IdentifierManager):
        self.structure_transformer = CairoSerializer(identifier_manager)
        self.abi = abi

    def from_python(self, *args, **kwargs) -> Tuple[List[int], Dict[str, List[int]]]:
        return self.structure_transformer.from_python(
            self.abi["inputs"], *args, **kwargs
        )

    def to_python(self, values: CairoData) -> NamedTuple:
        return self.structure_transformer.to_python(self.abi["outputs"], values)


def DataTransformer(*args, **kwargs):
    warnings.warn("DataTransformer is deprecated. Use FunctionCallSerializer instead")

    return FunctionCallSerializer(*args, **kwargs)
