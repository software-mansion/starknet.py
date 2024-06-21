from dataclasses import dataclass
from typing import Dict, List, Optional, Union, cast

from marshmallow import Schema, fields, post_load

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.hash.hash_method import HashMethod
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.hash.utils import compute_hash_on_elements
from starknet_py.net.models.typed_data import DomainDict, Revision, TypedDataDict
from starknet_py.net.schemas.common import ChainIdField, RevisionField


@dataclass(frozen=True)
class Parameter:
    """
    Dataclass representing a Parameter object
    """

    name: str
    type: str

    def to_dict(self) -> dict:
        """
        Create Parameter dictionary from dataclass.

        :return: Parameter dictionary.
        """
        return cast(Dict, ParameterSchema().dump(obj=self))


@dataclass
class Domain:
    """
    Dataclass representing a domain object (StarkNetDomain, StarknetDomain)
    """

    name: str
    version: str
    chain_id: Union[str, int]
    revision: Optional[Revision] = None

    def __post_init__(self):
        self.resolved_revision = (
            Revision(self.revision) if self.revision else Revision.V0
        )
        self.separator_name = self._resolve_separator_name()

    def _resolve_separator_name(self):
        if self.resolved_revision == Revision.V0:
            return "StarkNetDomain"
        return "StarknetDomain"

    @staticmethod
    def from_dict(data: DomainDict) -> "Domain":
        """
        Create Domain dataclass from dictionary.

        :param data: Domain dictionary.
        :return: Domain dataclass instance.
        """
        return cast(Domain, DomainSchema().load(data))

    def to_dict(self) -> dict:
        """
        Create Domain dictionary from dataclass.

        :return: Domain dictionary.
        """
        return cast(Dict, DomainSchema().dump(obj=self))


@dataclass(frozen=True)
class TypedData:
    """
    Dataclass representing a TypedData object
    """

    types: Dict[str, List[Parameter]]
    primary_type: str
    domain: Domain
    message: dict

    def __post_init__(self):
        self._verify_types()

    @property
    def _hash_method(self) -> HashMethod:
        if self.domain.resolved_revision == Revision.V0:
            return HashMethod.PEDERSEN
        return HashMethod.POSEIDON

    @staticmethod
    def from_dict(data: TypedDataDict) -> "TypedData":
        """
        Create TypedData dataclass from dictionary.

        :param data: TypedData dictionary.
        :return: TypedData dataclass instance.
        """
        return cast(TypedData, TypedDataSchema().load(data))

    def to_dict(self) -> dict:
        """
        Create TypedData dictionary from dataclass.

        :return: TypedData dictionary.
        """

        types_dict = {}
        for type_name, params in self.types.items():
            types_dict[type_name] = [param.to_dict() for param in params]

        return {
            "types": types_dict,
            "primaryType": self.primary_type,
            "domain": self.domain.to_dict(),
            "message": self.message,
        }

    def _is_struct(self, type_name: str) -> bool:
        return type_name in self.types

    def _encode_value(self, type_name: str, value: Union[int, str, dict, list]) -> int:
        if is_pointer(type_name) and isinstance(value, list):
            type_name = strip_pointer(type_name)

            if self._is_struct(type_name):
                return compute_hash_on_elements(
                    [self.struct_hash(type_name, data) for data in value]
                )
            return compute_hash_on_elements([int(get_hex(val), 16) for val in value])

        if self._is_struct(type_name) and isinstance(value, dict):
            return self.struct_hash(type_name, value)

        value = cast(Union[int, str], value)
        return int(get_hex(value), 16)

    def _encode_data(self, type_name: str, data: dict) -> List[int]:
        values = []
        for param in self.types[type_name]:
            encoded_value = self._encode_value(param.type, data[param.name])
            values.append(encoded_value)

        return values

    def _verify_types(self):
        reserved_type_names = ["felt", "felt*", "string", "selector"]

        for type_name in reserved_type_names:
            if type_name in self.types:
                raise ValueError(f"Reserved type name: {type_name}")

    def _get_dependencies(self, type_name: str) -> List[str]:
        if type_name not in self.types:
            # type_name is a primitive type, has no dependencies
            return []

        dependencies = set()

        def collect_deps(type_name: str) -> None:
            for param in self.types[type_name]:
                fixed_type = strip_pointer(param.type)
                if fixed_type in self.types and fixed_type not in dependencies:
                    dependencies.add(fixed_type)
                    # recursive call
                    collect_deps(fixed_type)

        # collect dependencies into a set
        collect_deps(type_name)
        return [type_name, *list(dependencies)]

    def _encode_type(self, type_name: str) -> str:
        primary, *dependencies = self._get_dependencies(type_name)
        types = [primary, *sorted(dependencies)]

        def make_dependency_str(dependency):
            lst = [
                f"{escape(t.name, self.domain.resolved_revision)}:{escape(t.type, self.domain.resolved_revision)}"
                for t in self.types[dependency]
            ]
            return (
                f"{escape(dependency, self.domain.resolved_revision)}({','.join(lst)})"
            )

        return "".join([make_dependency_str(x) for x in types])

    def type_hash(self, type_name: str) -> int:
        """
        Calculate the hash of a type name.

        :param type_name: Name of the type.
        :return: Hash of the type name.
        """
        return get_selector_from_name(self._encode_type(type_name))

    def struct_hash(self, type_name: str, data: dict) -> int:
        """
        Calculate the hash of a struct.

        :param type_name: Name of the type.
        :param data: Data defining the struct.
        :return: Hash of the struct.
        """
        return self._hash_method.hash(
            [self.type_hash(type_name), *self._encode_data(type_name, data)]
        )

    def message_hash(self, account_address: int) -> int:
        """
        Calculate the hash of the message.

        :param account_address: Address of an account.
        :return: Hash of the message.
        """
        message = [
            encode_shortstring("StarkNet Message"),
            self.struct_hash(self.domain.separator_name, self.domain.to_dict()),
            account_address,
            self.struct_hash(self.primary_type, self.message),
        ]

        return self._hash_method.hash(message)


def get_hex(value: Union[int, str]) -> str:
    if isinstance(value, int):
        return hex(value)
    if isinstance(value, Revision):
        return hex(value.value)
    if value[:2] == "0x":
        return value
    if value.isnumeric():
        return hex(int(value))
    return hex(encode_shortstring(value))


def is_pointer(value: str) -> bool:
    return len(value) > 0 and value[-1] == "*"


def strip_pointer(value: str) -> str:
    if is_pointer(value):
        return value[:-1]
    return value


def escape(s: str, revision: Revision) -> str:
    if revision == Revision.V0:
        return s
    return f'"{s}"'


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
        return TypedData(
            types=data["types"],
            primary_type=data["primary_type"],
            domain=Domain.from_dict(data["domain"]),
            message=data["message"],
        )


class DomainSchema(Schema):
    name = fields.String(data_key="name", required=True)
    version = fields.String(data_key="version", required=True)
    chain_id = ChainIdField(attribute="chain_id", data_key="chainId", required=True)
    revision = RevisionField(data_key="revision", required=False)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Domain:
        return Domain(
            name=data["name"],
            version=data["version"],
            chain_id=data["chain_id"],
            revision=data.get("revision"),
        )
