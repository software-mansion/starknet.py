from marshmallow import fields, post_load

from starknet_py.net.client_models import (
    ComputationResources,
    DataResources,
    EstimatedFee,
    ExecutionResources,
)
from starknet_py.net.schemas.common import Felt, PriceUnitField
from starknet_py.utils.schema import Schema


class ComputationResourcesSchema(Schema):
    steps = fields.Integer(data_key="steps", required=True)
    memory_holes = fields.Integer(data_key="memory_holes", load_default=None)
    range_check_builtin_applications = fields.Integer(
        data_key="range_check_builtin_applications", load_default=None
    )
    pedersen_builtin_applications = fields.Integer(
        data_key="pedersen_builtin_applications", load_default=None
    )
    poseidon_builtin_applications = fields.Integer(
        data_key="poseidon_builtin_applications", load_default=None
    )
    ec_op_builtin_applications = fields.Integer(
        data_key="ec_op_builtin_applications", load_default=None
    )
    ecdsa_builtin_applications = fields.Integer(
        data_key="ecdsa_builtin_applications", load_default=None
    )
    bitwise_builtin_applications = fields.Integer(
        data_key="bitwise_builtin_applications", load_default=None
    )
    keccak_builtin_applications = fields.Integer(
        data_key="keccak_builtin_applications", load_default=None
    )
    segment_arena_builtin = fields.Integer(
        data_key="segment_arena_builtin", load_default=None
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ComputationResources:
        return ComputationResources(**data)


class DataResourcesSchema(Schema):
    l1_gas = fields.Integer(data_key="l1_gas", required=True)
    l1_data_gas = fields.Integer(data_key="l1_data_gas", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> DataResources:
        return DataResources(**data)


class ExecutionResourcesSchema(ComputationResourcesSchema):
    data_availability = fields.Nested(
        DataResourcesSchema(), data_key="data_availability", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ExecutionResources:
        return ExecutionResources(**data)


class EstimatedFeeSchema(Schema):
    gas_consumed = Felt(data_key="gas_consumed", required=True)
    gas_price = Felt(data_key="gas_price", required=True)
    data_gas_consumed = Felt(data_key="data_gas_consumed", required=True)
    data_gas_price = Felt(data_key="data_gas_price", required=True)
    overall_fee = Felt(data_key="overall_fee", required=True)
    unit = PriceUnitField(data_key="unit", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EstimatedFee:
        return EstimatedFee(**data)
