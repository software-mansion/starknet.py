from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union, cast

from marshmallow import Schema, fields, post_load

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.hash.hash_method import HashMethod
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.hash.utils import compute_hash_on_elements
from starknet_py.net.client_utils import _to_rpc_felt
from starknet_py.net.models.typed_data import DomainDict, Revision, TypedDataDict
from starknet_py.net.schemas.common import ChainIdField, RevisionField
from starknet_py.utils.merkle_tree import MerkleTree


@dataclass(frozen=True)
class Parameter:
    """
    Dataclass representing a Parameter object
    """

    name: str
    type: str
    contains: Optional[str] = None

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
class TypeContext:
    """
    Dataclass representing a Context object
    """

    parent: str
    key: str


class BasicType(Enum):
    FELT = "felt"
    SELECTOR = "selector"
    MERKLE_TREE = "merkletree"
    SHORT_STRING = "shortstring"
    STRING = "string"
    CONTRACT_ADDRESS = "ContractAddress"
    CLASS_HASH = "ClassHash"
    BOOL = "bool"


@dataclass(frozen=True)
class TypedData:
    """
    Dataclass representing a TypedData object
    """

    types: Dict[str, List[Parameter]]
    primary_type: str
    domain: Domain
    message: dict

    _basic_types_v0 = {
        BasicType.FELT,
        BasicType.BOOL,
        BasicType.STRING,
        BasicType.SELECTOR,
        BasicType.MERKLE_TREE,
    }
    _basic_types_v1 = _basic_types_v0.union(
        {BasicType.CONTRACT_ADDRESS, BasicType.CLASS_HASH, BasicType.SHORT_STRING}
    )

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

    def _get_basic_types(self) -> set[BasicType]:
        if self.domain.resolved_revision == Revision.V0:
            return self._basic_types_v0
        return self._basic_types_v1

    def _is_struct(self, type_name: str) -> bool:
        return type_name in self.types

    # pylint: disable=too-many-return-statements
    def _encode_value(
        self,
        type_name: str,
        value: Union[int, str, dict, list],
        context: Optional[TypeContext] = None,
    ) -> int:
        if isinstance(value, Revision):
            value = value.value

        if type_name in self.types and isinstance(value, dict):
            return self.struct_hash(type_name, value)

        if is_pointer(type_name) and isinstance(value, list):
            type_name = strip_pointer(type_name)
            hashes = [self._encode_value(type_name, val) for val in value]
            return compute_hash_on_elements(hashes)

        basic_types = [bt.value for bt in BasicType]
        if type_name not in basic_types:
            raise ValueError(f"Type [{type_name}] is not defined in types.")

        basic_type = BasicType(type_name)

        if basic_type == BasicType.FELT and isinstance(value, Union[int, str]):
            return int(get_hex(value), 16)

        if (basic_type, self.domain.resolved_revision) in [
            (BasicType.STRING, Revision.V0),
            (BasicType.SHORT_STRING, Revision.V1),
            (BasicType.STRING, Revision.V1),
            (BasicType.CONTRACT_ADDRESS, Revision.V1),
            (BasicType.CLASS_HASH, Revision.V1),
        ] and isinstance(value, Union[int, str]):
            return int(get_hex(value), 16)

        if basic_type == BasicType.BOOL and isinstance(value, Union[bool, str, int]):
            return encode_bool(value)

        if basic_type == BasicType.SELECTOR and isinstance(value, str):
            return prepare_selector(value)

        if basic_type == BasicType.MERKLE_TREE and isinstance(value, list):
            if context is None:
                raise ValueError(f"Context is not provided for '{type_name}' type.")
            return self._prepare_merkle_tree_root(value, context)

        raise ValueError(
            f"Error occurred while encoding value with type name {type_name}."
        )

    def _encode_data(self, type_name: str, data: dict) -> List[int]:
        values = []
        for param in self.types[type_name]:
            encoded_value = self._encode_value(
                param.type,
                data[param.name],
                TypeContext(parent=type_name, key=param.name),
            )
            values.append(encoded_value)

        return values

    def _verify_types(self):
        if self.domain.separator_name not in self.types:
            raise ValueError(f"Types must contain '{self.domain.separator_name}'.")

        basic_types = set(map(lambda bt: bt.value, self._get_basic_types()))

        referenced_types = [
            parameter for type_name in self.types for parameter in self.types[type_name]
        ]
        referenced_types = [
            ref_type.contains
            if ref_type.contains is not None
            else strip_pointer(ref_type.type)
            for ref_type in referenced_types
        ] + [self.domain.separator_name, self.primary_type]

        for type_name in self.types:
            if type_name in basic_types:
                raise ValueError(f"Reserved type name: {type_name}")

            if not type_name:
                raise ValueError("Type names cannot be empty.")

            if is_pointer(type_name):
                raise ValueError(f"Type names cannot end in *. {type_name} was found.")

            if type_name not in referenced_types:
                raise ValueError(
                    f"Dangling types are not allowed. Unreferenced type {type_name} was found."
                )

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
        return self._hash_method.hash_many(
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

        return self._hash_method.hash_many(message)

    def _prepare_merkle_tree_root(self, value: List, context: TypeContext) -> int:
        merkle_tree_type = self._get_merkle_tree_leaves_type(context)
        struct_hashes = list(
            map(lambda struct: self._encode_value(merkle_tree_type, struct), value)
        )

        return MerkleTree(struct_hashes, self._hash_method).root_hash

    def _get_merkle_tree_leaves_type(self, context: TypeContext) -> str:
        parent, key = context.parent, context.key

        if parent not in self.types:
            raise ValueError(f"Parent {parent} is not defined in types.")

        parent_type = self.types[parent]

        # target_type = next((item for item in parent_type if item.type == key), None)
        target_type = None
        for item in parent_type:
            if item.name == key:
                target_type = item
                break
        if target_type is None:
            raise ValueError(
                f"Key {key} is not defined in type {parent} or multiple definitions are present."
            )

        if not target_type.contains:
            raise ValueError("Missing 'contains' field in target type.")

        return target_type.contains


def get_hex(value: Union[int, str]) -> str:
    if isinstance(value, int):
        return hex(value)
    if value[:2] == "0x":
        return value
    if value.isnumeric():
        return hex(int(value))
    return hex(encode_shortstring(value))


def is_pointer(value: str) -> bool:
    return value.endswith("*")


def strip_pointer(value: str) -> str:
    if is_pointer(value):
        return value[:-1]
    return value


def escape(s: str, revision: Revision) -> str:
    if revision == Revision.V0:
        return s
    return f'"{s}"'


def prepare_selector(name: str) -> int:
    try:
        return int(_to_rpc_felt(name), 16)
    except ValueError:
        return get_selector_from_name(name)


def encode_bool(value: Union[bool, str, int]) -> int:
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int) and value in (0, 1):
        return value
    if isinstance(value, str) and value in ("0", "1"):
        return int(value)
    if isinstance(value, str) and value in ("false", "true"):
        return 0 if value == "false" else 1
    if isinstance(value, str) and value in ("0x0", "0x1"):
        return int(value, 16)
    raise ValueError(f"Expected boolean value, got [{value}].")


# pylint: disable=unused-argument
# pylint: disable=no-self-use


class ParameterSchema(Schema):
    name = fields.String(data_key="name", required=True)
    type = fields.String(data_key="type", required=True)
    contains = fields.String(data_key="contains", required=False)

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
