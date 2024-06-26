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
from starknet_py.net.schemas.common import RevisionField
from starknet_py.utils.merkle_tree import MerkleTree


@dataclass(frozen=True)
class Parameter:
    """
    Dataclass representing a Parameter object
    """

    name: str
    type: str
    contains: Optional[str] = None


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

        return cast(Dict, TypedDataSchema().dump(obj=self))

    def _is_struct(self, type_name: str) -> bool:
        return type_name in self.types

    def _encode_value(
        self,
        type_name: str,
        value: Union[int, str, dict, list],
        context: Optional[TypeContext] = None,
    ) -> int:
        if type_name in self.types and isinstance(value, dict):
            return self.struct_hash(type_name, value)

        if is_pointer(type_name) and isinstance(value, list):
            type_name = strip_pointer(type_name)
            hashes = [self._encode_value(type_name, val) for val in value]
            return compute_hash_on_elements(hashes)

        basic_type = BasicType(type_name)

        if basic_type == BasicType.MERKLE_TREE and isinstance(value, list):
            if context is None:
                raise ValueError(f"Context is not provided for '{type_name}' type.")
            return self._prepare_merkle_tree_root(value, context)

        if basic_type in (BasicType.FELT, BasicType.SHORT_STRING) and isinstance(
            value, (int, str, Revision)
        ):
            return int(get_hex(value), 16)

        if basic_type == BasicType.SELECTOR and isinstance(value, str):
            return prepare_selector(value)

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
        reserved_type_names = ["felt", "felt*", "string", "selector", "merkletree"]

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

        target_type = next((item for item in parent_type if item.name == key), None)
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
    return len(value) > 0 and value[-1] == "*"


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


class BasicType(Enum):
    FELT = "felt"
    SELECTOR = "selector"
    MERKLE_TREE = "merkletree"
    SHORT_STRING = "shortstring"


# pylint: disable=unused-argument
# pylint: disable=no-self-use


class ParameterSchema(Schema):
    name = fields.String(data_key="name", required=True)
    type = fields.String(data_key="type", required=True)
    contains = fields.String(data_key="contains", required=False)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Parameter:
        return Parameter(**data)


class DomainSchema(Schema):
    name = fields.String(data_key="name", required=True)
    version = fields.String(data_key="version", required=True)
    chain_id = fields.String(attribute="chain_id", data_key="chainId", required=True)
    revision = RevisionField(data_key="revision", required=False)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Domain:
        return Domain(
            name=data["name"],
            version=data["version"],
            chain_id=data["chain_id"],
            revision=data.get("revision"),
        )


class TypedDataSchema(Schema):
    types = fields.Dict(
        data_key="types",
        keys=fields.Str(),
        values=fields.List(fields.Nested(ParameterSchema())),
    )
    primary_type = fields.String(data_key="primaryType", required=True)
    domain = fields.Nested(DomainSchema, required=True)
    message = fields.Dict(data_key="message", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> TypedData:
        return TypedData(
            types=data["types"],
            primary_type=data["primary_type"],
            domain=data["domain"],
            message=data["message"],
        )
