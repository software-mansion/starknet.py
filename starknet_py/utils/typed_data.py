import re
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union, cast

from marshmallow import Schema, fields, post_load

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.constants import FIELD_PRIME
from starknet_py.hash.hash_method import HashMethod
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_utils import _to_rpc_felt
from starknet_py.net.models.typed_data import DomainDict, Revision, TypedDataDict
from starknet_py.net.schemas.common import RevisionField
from starknet_py.serialization.data_serializers import ByteArraySerializer
from starknet_py.utils.merkle_tree import MerkleTree


@dataclass(frozen=True)
class Parameter(ABC):
    name: str
    type: str


@dataclass(frozen=True)
class StandardParameter(Parameter):
    pass


@dataclass(frozen=True)
class MerkleTreeParameter(Parameter):
    type: str = field(default="merkletree", init=False)
    contains: str


@dataclass(frozen=True)
class EnumParameter(Parameter):
    type: str = field(default="enum", init=False)
    contains: str


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
    ENUM = "enum"
    SHORT_STRING = "shortstring"
    STRING = "string"
    CONTRACT_ADDRESS = "ContractAddress"
    CLASS_HASH = "ClassHash"
    BOOL = "bool"
    U128 = "u128"
    I128 = "i128"
    TIMESTAMP = "timestamp"


class PresetType(Enum):
    U256 = "u256"
    TOKEN_AMOUNT = "TokenAmount"
    NFT_ID = "NftId"


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
    def _all_types(self):
        preset_types = _get_preset_types(self.domain.resolved_revision)
        return {
            **preset_types,
            **self.types,
        }

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

    def _encode_value_v1(
        self,
        basic_type: BasicType,
        value: Union[int, str, dict],
        type_name: str,
        context: Optional[TypeContext] = None,
    ) -> Optional[int]:
        if basic_type in (
            BasicType.FELT,
            BasicType.SHORT_STRING,
            BasicType.CONTRACT_ADDRESS,
            BasicType.CLASS_HASH,
        ) and isinstance(value, (int, str)):
            return parse_felt(value)

        if basic_type in (
            BasicType.U128,
            BasicType.TIMESTAMP,
        ) and isinstance(value, (int, str)):
            return encode_u128(value)

        if basic_type == BasicType.I128 and isinstance(value, (int, str)):
            return encode_i128(value)

        if basic_type == BasicType.STRING and isinstance(value, str):
            return self._encode_long_string(value)

        if basic_type == BasicType.ENUM and isinstance(value, dict):
            if context is None:
                raise ValueError(f"Context is not provided for '{type_name}' type.")
            return self._encode_enum(value, context)

        return None

    # pylint: disable=no-self-use
    def _encode_value_v0(
        self,
        basic_type: BasicType,
        value: Union[int, str],
    ) -> Optional[int]:
        if basic_type in (
            BasicType.FELT,
            BasicType.STRING,
        ) and isinstance(value, (int, str)):
            return parse_felt(value)

        return None

    def _encode_value(
        self,
        type_name: str,
        value: Union[int, str, dict, list],
        context: Optional[TypeContext] = None,
    ) -> int:
        if type_name in self._all_types and isinstance(value, dict):
            return self.struct_hash(type_name, value)

        if is_pointer(type_name) and isinstance(value, list):
            type_name = strip_pointer(type_name)
            hashes = [self._encode_value(type_name, val) for val in value]
            return self._hash_method.hash_many(hashes)

        if type_name not in _get_basic_type_names(self.domain.resolved_revision):
            raise ValueError(f"Type [{type_name}] is not defined in types.")

        basic_type = BasicType(type_name)

        encoded_value = None
        if self.domain.resolved_revision == Revision.V0 and isinstance(
            value, (str, int)
        ):
            encoded_value = self._encode_value_v0(basic_type, value)
        elif self.domain.resolved_revision == Revision.V1 and isinstance(
            value, (str, int, dict)
        ):
            encoded_value = self._encode_value_v1(basic_type, value, type_name, context)

        if encoded_value is not None:
            return encoded_value

        if basic_type == BasicType.BOOL and isinstance(value, (bool, str, int)):
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
        for param in self._all_types[type_name]:
            encoded_value = self._encode_value(
                param.type,
                data[param.name],
                TypeContext(parent=type_name, key=param.name),
            )
            values.append(encoded_value)

        return values

    # pylint: disable=too-many-branches
    def _verify_types(self):
        if self.domain.separator_name not in self.types:
            raise ValueError(f"Types must contain '{self.domain.separator_name}'.")

        referenced_types = set()
        for type_name in self.types:
            for ref_type in self.types[type_name]:
                if isinstance(ref_type, (EnumParameter, MerkleTreeParameter)):
                    referenced_types.add(ref_type.contains)
                elif is_enum_variant_type(ref_type.type):
                    referenced_types.update(_extract_enum_types(ref_type.type))
                else:
                    referenced_types.add(strip_pointer(ref_type.type))

        referenced_types.update([self.domain.separator_name, self.primary_type])

        basic_type_names = _get_basic_type_names(self.domain.resolved_revision)
        preset_type_names = _get_preset_types(self.domain.resolved_revision).keys()

        for type_name in self.types:
            if not type_name:
                raise ValueError("Type names cannot be empty.")

            if type_name in basic_type_names:
                raise ValueError(
                    f"Types must not contain basic types. [{type_name}] was found."
                )

            if type_name in preset_type_names:
                raise ValueError(
                    f"Types must not contain preset types. [{type_name}] was found."
                )

            if is_pointer(type_name):
                raise ValueError(
                    f"Type names cannot end in *. [{type_name}] was found."
                )

            if is_enum_variant_type(type_name):
                raise ValueError(
                    f"Type names cannot be enclosed in parentheses. [{type_name}] was found."
                )

            if "," in type_name:
                raise ValueError(
                    f"Type names cannot contain commas. [{type_name}] was found."
                )

            if type_name not in referenced_types:
                raise ValueError(
                    f"Dangling types are not allowed. Unreferenced type [{type_name}] was found."
                )

            for ref_type in self.types[type_name]:
                if isinstance(ref_type, EnumParameter):
                    self._validate_enum_type()

    def _validate_enum_type(self):
        if self.domain.resolved_revision != Revision.V1:
            raise ValueError(
                f"'{BasicType.ENUM.name}' basic type is not supported in revision "
                f"{self.domain.resolved_revision.value}."
            )

    def _get_dependencies(self, type_name: str) -> List[str]:
        dependencies = [type_name]
        to_visit = [type_name]

        while to_visit:
            current_type = to_visit.pop(0)
            params = self._all_types.get(current_type, [])

            for param in params:
                if isinstance(param, EnumParameter):
                    extracted_types = [param.contains]
                elif is_enum_variant_type(param.type):
                    extracted_types = _extract_enum_types(param.type)
                else:
                    extracted_types = [param.type]

                extracted_types = [
                    strip_pointer(extr_type) for extr_type in extracted_types
                ]
                for extracted_type in extracted_types:
                    if (
                        extracted_type in self._all_types
                        and extracted_type not in dependencies
                    ):
                        dependencies.append(extracted_type)
                        to_visit.append(extracted_type)

        return list(dependencies)

    def _encode_type(self, type_name: str) -> str:
        primary, *dependencies = self._get_dependencies(type_name)
        types = [primary, *sorted(dependencies)]

        def encode_dependency(dependency: str) -> str:
            def escape(s: str) -> str:
                if self.domain.resolved_revision == Revision.V0:
                    return s
                return f'"{s}"'

            if dependency not in self._all_types:
                raise ValueError(f"Dependency [{dependency}] is not defined in types.")

            encoded_params = []
            for param in self._all_types[dependency]:
                target_type = (
                    param.contains
                    if isinstance(param, EnumParameter)
                    and self.domain.resolved_revision == Revision.V1
                    else param.type
                )

                if is_enum_variant_type(target_type):
                    type_str = _extract_enum_types(target_type)
                    type_str = f"({','.join([escape(x) for x in type_str])})"

                else:
                    type_str = escape(target_type)

                encoded_params.append(f"{escape(param.name)}:{type_str}")
            encoded_params = ",".join(encoded_params)

            return f"{escape(dependency)}({encoded_params})"

        return "".join([encode_dependency(x) for x in types])

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
        struct_hashes = [
            self._encode_value(merkle_tree_type, struct) for struct in value
        ]

        return MerkleTree(struct_hashes, self._hash_method).root_hash

    def _get_merkle_tree_leaves_type(self, context: TypeContext) -> str:
        target_type = self._resolve_type(context)

        if not isinstance(target_type, MerkleTreeParameter):
            raise ValueError("Target type is not a merkletree type.")

        return target_type.contains

    def _resolve_type(self, context: TypeContext) -> Parameter:
        parent, key = context.parent, context.key

        if parent not in self._all_types:
            raise ValueError(f"Parent {parent} is not defined in types.")

        parent_type = self._all_types[parent]

        target_type = next((item for item in parent_type if item.name == key), None)
        if target_type is None:
            raise ValueError(
                f"Key {key} is not defined in type {parent} or multiple definitions are present."
            )

        if not isinstance(target_type, (EnumParameter, MerkleTreeParameter)):
            raise ValueError("Target type is not an enum or merkletree type.")
        return target_type

    def _encode_enum(self, value: dict, context: TypeContext):
        if len(value.keys()) != 1:
            raise ValueError(
                f"'{BasicType.ENUM.name}' value must contain a single variant."
            )

        variant_name, variant_data = next(iter(value.items()))
        variants = self._get_enum_variants(context)
        variant_definition = next(
            (item for item in variants if item.name == variant_name), None
        )

        if variant_definition is None:
            raise ValueError(
                f"Variant [{variant_name}] is not defined in '${BasicType.ENUM.name}' "
                f"type [{context.key}] or multiple definitions are present."
            )

        encoded_subtypes = []
        extracted_enum_types = _extract_enum_types(variant_definition.type)

        for i, subtype in enumerate(extracted_enum_types):
            subtype_data = variant_data[i]
            encoded_subtypes.append(self._encode_value(subtype, subtype_data))

        variant_index = variants.index(variant_definition)
        return self._hash_method.hash_many([variant_index, *encoded_subtypes])

    def _get_enum_variants(self, context: TypeContext) -> List[Parameter]:
        enum_type = self._resolve_type(context)
        if not isinstance(enum_type, EnumParameter):
            raise ValueError(f"Type [{context.key}] is not an enum.")
        if enum_type.contains not in self._all_types:
            raise ValueError(f"Type [{enum_type.contains}] is not defined in types")

        return self._all_types[enum_type.contains]

    def _encode_long_string(self, value: str) -> int:
        byte_array_serializer = ByteArraySerializer()
        serialized_values = byte_array_serializer.serialize(value)
        return self._hash_method.hash_many(serialized_values)


def _extract_enum_types(value: str) -> List[str]:
    if not is_enum_variant_type(value):
        raise ValueError(f"Type [{value}] is not an enum.")

    value = value[1:-1]
    if not value:
        return []

    return value.split(",")


def parse_felt(value: Union[int, str]) -> int:
    if isinstance(value, int):
        return value
    if value.startswith("0x"):
        return int(value, 16)
    if value.isnumeric():
        return int(value)
    return encode_shortstring(value)


def is_pointer(value: str) -> bool:
    return value.endswith("*")


def strip_pointer(value: str) -> str:
    if is_pointer(value):
        return value[:-1]
    return value


def is_enum_variant_type(value: str) -> bool:
    return value.startswith("(") and value.endswith(")")


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


def is_digit_string(s: str, signed=False) -> bool:
    if signed:
        return bool(re.fullmatch(r"-?\d+", s))
    return bool(re.fullmatch(r"\d+", s))


def encode_u128(value: Union[str, int]) -> int:
    def is_in_range(n: int):
        return 0 <= n < 2**128

    if isinstance(value, str) and value.startswith("0x"):
        int_value = int(value, 16)
    elif isinstance(value, str) and is_digit_string(value):
        int_value = int(value)
    elif isinstance(value, int):
        int_value = value
    else:
        raise ValueError(f"Value [{value}] is not a valid number.")

    if is_in_range(int_value):
        return int_value
    raise ValueError(f"Value [{value}] is out of range for '{BasicType.U128}'.")


def encode_i128(value: Union[str, int]) -> int:
    def is_in_range(n: int):
        return (n < 2**127) or (n >= (FIELD_PRIME - (2**127)))

    if isinstance(value, str) and value.startswith("0x"):
        int_value = int(value, 16)
    elif isinstance(value, str) and is_digit_string(value, True):
        int_value = int(value)
    elif isinstance(value, int):
        int_value = value
    else:
        raise ValueError(f"Value [{value}] is not a valid number.")

    if abs(int_value) >= FIELD_PRIME:
        raise ValueError(
            f"Values outside the range (-FIELD_PRIME, FIELD_PRIME) are not allowed, [{value}] given."
        )
    int_value %= FIELD_PRIME

    if is_in_range(int_value):
        return int_value
    raise ValueError(f"Value [{value}] is out of range for '{BasicType.I128}'.")


def _get_basic_type_names(revision: Revision) -> List[str]:
    basic_types_v0 = [
        BasicType.FELT,
        BasicType.SELECTOR,
        BasicType.MERKLE_TREE,
        BasicType.STRING,
        BasicType.BOOL,
    ]

    basic_types_v1 = list(BasicType)

    basic_types = basic_types_v0 if revision == Revision.V0 else basic_types_v1
    return [basic_type.value for basic_type in basic_types]


def _get_preset_types(
    revision: Revision,
) -> Dict[str, List[StandardParameter]]:
    if revision == Revision.V0:
        return {}

    return {
        PresetType.U256.value: [
            StandardParameter(name="low", type="u128"),
            StandardParameter(name="high", type="u128"),
        ],
        PresetType.TOKEN_AMOUNT.value: [
            StandardParameter(name="token_address", type="ContractAddress"),
            StandardParameter(name="amount", type="u256"),
        ],
        PresetType.NFT_ID.value: [
            StandardParameter(name="collection_address", type="ContractAddress"),
            StandardParameter(name="token_id", type="u256"),
        ],
    }


# pylint: disable=unused-argument
# pylint: disable=no-self-use


class ParameterSchema(Schema):
    name = fields.String(data_key="name", required=True)
    type = fields.String(data_key="type", required=True)
    contains = fields.String(data_key="contains", required=False)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Parameter:
        type_val = data["type"]

        if type_val == BasicType.MERKLE_TREE.value:
            return MerkleTreeParameter(name=data["name"], contains=data["contains"])

        if type_val == BasicType.ENUM.value:
            return EnumParameter(name=data["name"], contains=data["contains"])

        return StandardParameter(name=data["name"], type=type_val)


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
