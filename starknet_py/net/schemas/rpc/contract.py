import json

from marshmallow import EXCLUDE
from marshmallow import Schema as MarshmallowSchema
from marshmallow import SchemaOpts, ValidationError, fields, post_load

from starknet_py.abi.v0.schemas import ContractAbiEntrySchema
from starknet_py.net.client_models import (
    CasmClassEntryPoint,
    CasmClassEntryPointsByType,
    DeployedContract,
    DeprecatedCompiledContract,
    DeprecatedContractClass,
    EntryPoint,
    EntryPointsByType,
    SierraCompiledContract,
    SierraContractClass,
    SierraEntryPoint,
    SierraEntryPointsByType,
    SyncStatus,
)
from starknet_py.net.executable_models import CasmClass
from starknet_py.net.schemas.common import Felt, NumberAsHex
from starknet_py.net.schemas.rpc.executables_api import HintSchema
from starknet_py.utils.schema import ExcludeOpts, Schema


class SyncStatusSchema(Schema):
    starting_block_hash = Felt(data_key="starting_block_hash", required=True)
    starting_block_num = Felt(data_key="starting_block_num", required=True)
    current_block_hash = Felt(data_key="current_block_hash", required=True)
    current_block_num = Felt(data_key="current_block_num", required=True)
    highest_block_hash = Felt(data_key="highest_block_hash", required=True)
    highest_block_num = Felt(data_key="highest_block_num", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SyncStatus:
        return SyncStatus(**data)


class ContractDiffSchema(Schema):
    address = Felt(data_key="address", required=True)
    contract_hash = Felt(data_key="contract_hash", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeployedContract:
        return DeployedContract(**data)


class SierraEntryPointSchema(Schema):
    selector = Felt(data_key="selector", required=True)
    function_idx = fields.Integer(data_key="function_idx", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraEntryPoint:
        return SierraEntryPoint(**data)


class EntryPointSchema(Schema):
    offset = NumberAsHex(data_key="offset", required=True)
    selector = Felt(data_key="selector", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EntryPoint:
        return EntryPoint(**data)


class SierraEntryPointsByTypeSchema(Schema):
    constructor = fields.List(
        fields.Nested(SierraEntryPointSchema()), data_key="CONSTRUCTOR", required=True
    )
    external = fields.List(
        fields.Nested(SierraEntryPointSchema()), data_key="EXTERNAL", required=True
    )
    l1_handler = fields.List(
        fields.Nested(SierraEntryPointSchema()), data_key="L1_HANDLER", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraEntryPointsByType:
        return SierraEntryPointsByType(**data)


class EntryPointsByTypeSchema(Schema):
    constructor = fields.List(
        fields.Nested(EntryPointSchema()), data_key="CONSTRUCTOR", required=True
    )
    external = fields.List(
        fields.Nested(EntryPointSchema()), data_key="EXTERNAL", required=True
    )
    l1_handler = fields.List(
        fields.Nested(EntryPointSchema()), data_key="L1_HANDLER", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> EntryPointsByType:
        return EntryPointsByType(**data)


class SierraContractClassSchema(Schema):
    sierra_program = fields.List(Felt(), data_key="sierra_program", required=True)
    contract_class_version = fields.String(
        data_key="contract_class_version", required=True
    )
    entry_points_by_type = fields.Nested(
        SierraEntryPointsByTypeSchema(), data_key="entry_points_by_type", required=True
    )
    abi = fields.String(data_key="abi", required=False)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraContractClass:
        return SierraContractClass(**data)


class ContractClassSchema(Schema):
    program = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(load_default=None),
        data_key="program",
        required=True,
    )
    entry_points_by_type = fields.Nested(
        EntryPointsByTypeSchema(), data_key="entry_points_by_type", required=True
    )
    abi = fields.List(fields.Dict(), data_key="abi")

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeprecatedContractClass:
        return DeprecatedContractClass(**data)


class DeprecatedContractClassSchema(Schema):
    program = fields.String(data_key="program", required=True)
    entry_points_by_type = fields.Nested(
        EntryPointsByTypeSchema(), data_key="entry_points_by_type", required=True
    )
    abi = fields.List(
        fields.Nested(ContractAbiEntrySchema(unknown=EXCLUDE)), data_key="abi"
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeprecatedContractClass:
        return DeprecatedContractClass(**data)


class DeprecatedCompiledContractSchema(ContractClassSchema):
    abi = fields.List(fields.Dict(), data_key="abi", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DeprecatedCompiledContract:
        return DeprecatedCompiledContract(**data)


class CasmClassEntryPointSchema(Schema):
    selector = Felt(data_key="selector", required=True)
    offset = NumberAsHex(data_key="offset", required=True)
    builtins = fields.List(fields.String(), data_key="builtins")

    @post_load
    def make_dataclass(self, data, **kwargs) -> CasmClassEntryPoint:
        return CasmClassEntryPoint(**data)


class CasmClassEntryPointsByTypeSchema(Schema):
    constructor = fields.List(
        fields.Nested(CasmClassEntryPointSchema()),
        data_key="CONSTRUCTOR",
        required=True,
    )
    external = fields.List(
        fields.Nested(CasmClassEntryPointSchema()),
        data_key="EXTERNAL",
        required=True,
    )
    l1_handler = fields.List(
        fields.Nested(CasmClassEntryPointSchema()),
        data_key="L1_HANDLER",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> CasmClassEntryPointsByType:
        return CasmClassEntryPointsByType(**data)


# TODO(#1564): `CasmClassSchema` should inherit from `Schema` and shouldn't overwrite `OPTION_CLASS`
#  once issue is resolved.
class CasmClassSchema(MarshmallowSchema):
    OPTIONS_CLASS = ExcludeOpts
    prime = NumberAsHex(data_key="prime", required=True)
    bytecode = fields.List(Felt(), data_key="bytecode", required=True)
    bytecode_segment_lengths = fields.List(
        fields.Integer(), data_key="bytecode_segment_lengths", load_default=None
    )
    hints = fields.List(
        fields.Tuple(
            (fields.Integer(), fields.List(fields.Nested(HintSchema()))),
        ),
        data_key="hints",
        required=True,
    )
    compiler_version = fields.String(data_key="compiler_version", required=True)
    entry_points_by_type = fields.Nested(
        CasmClassEntryPointsByTypeSchema(),
        data_key="entry_points_by_type",
        required=True,
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> CasmClass:
        return CasmClass(**data)


class AbiField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str):
            return value
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return json.dumps(value)
        raise ValidationError("Field should be str or list[dict].")


class SierraCompiledContractSchema(SierraContractClassSchema):
    abi = AbiField(data_key="abi", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SierraCompiledContract:
        return SierraCompiledContract(**data)
