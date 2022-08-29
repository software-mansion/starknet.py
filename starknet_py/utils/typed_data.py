from dataclasses import dataclass
from typing import Union, Dict, List

from marshmallow import Schema, fields, post_load
from starkware.cairo.common.hash_state import compute_hash_on_elements
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.utils.typing import TypedDict


class StarkNetDomain(TypedDict):
    """
    TypedDict representing a StarkNetDomain object
    """

    name: str
    version: str
    chainId: Union[str, int]


@dataclass(frozen=True)
class Parameter:
    """
    Dataclass representing a Parameter object
    """

    name: str
    type: str


@dataclass(frozen=True)
class TypedData:
    """
    Dataclass representing a TypedData object
    """

    types: Dict[str, List[Parameter]]
    primary_type: str
    domain: StarkNetDomain
    message: dict

    def _encode_value(self, type_: str, value: Union[int, str]) -> str:
        if type_[-1] == "*":
            return compute_hash_on_elements(
                [self.struct_hash(type_[:-1], data) for data in value]
            )
        if type_ in self.types:
            return self.struct_hash(type_, value)
        return int(get_hex(value), 16)

    def _encode_data(self, type_: str, data: dict) -> List[str]:
        values = []
        for param in self.types[type_]:
            encoded_value = self._encode_value(param.type, data[param.name])
            values.append(encoded_value)

        return values

    def _get_dependencies(self, type_: str) -> List[str]:
        if type_ not in self.types:
            # type_ is a primitive type, has no dependencies
            return []

        dependencies = set()

        def collect_deps(type_: str) -> None:
            for param in self.types[type_]:
                # strip the pointer
                fixed_type = param.type[:-1] if param.type[-1] == "*" else param.type
                if fixed_type in self.types and fixed_type not in dependencies:
                    dependencies.add(fixed_type)
                    # recursive call
                    collect_deps(fixed_type)

        # collect dependencies into a set
        collect_deps(type_)
        return [type_, *list(dependencies)]

    def _encode_type(self, type_: str) -> str:
        [primary, *dependencies] = self._get_dependencies(type_)
        types = [primary, *sorted(dependencies)]

        def make_dependency_str(dependency):
            lst = [f"{t.name}:{t.type}" for t in self.types[dependency]]
            return f"{dependency}({','.join(lst)})"

        return "".join([make_dependency_str(x) for x in types])

    def type_hash(self, type_: str) -> int:
        return get_selector_from_name(self._encode_type(type_))

    def struct_hash(self, type_: str, data: dict) -> int:
        return compute_hash_on_elements(
            [self.type_hash(type_), *self._encode_data(type_, data)]
        )

    def message_hash(self, account_address: int) -> int:
        message = [
            encode_shortstring("StarkNet Message"),
            self.struct_hash("StarkNetDomain", self.domain),
            account_address,
            self.struct_hash(self.primary_type, self.message),
        ]

        return compute_hash_on_elements(message)


def get_hex(value: Union[int, str]):
    if isinstance(value, int):
        return hex(value)
    if value[:2] == "0x":
        return value
    if value.isnumeric():
        return hex(int(value))
    return hex(encode_shortstring(value))


# pylint: disable=unused-argument
# pylint: disable=no-self-use


class ParameterSchema(Schema):
    name = fields.String(data_key="name", required=True)
    type = fields.String(data_key="type", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Parameter:
        return Parameter(**data)


class TypedDataSchema(Schema):
    types = fields.Dict(
        data_key="types",
        keys=fields.Str(),
        values=fields.List(fields.Nested(ParameterSchema())),
    )
    primary_type = fields.String(data_key="primaryType", required=True)
    domain = fields.Dict(data_key="domain", required=True)
    message = fields.Dict(data_key="message", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> TypedData:
        return TypedData(**data)
