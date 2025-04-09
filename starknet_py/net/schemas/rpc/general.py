from marshmallow import fields, post_load

from starknet_py.net.client_models import EstimatedFee, ExecutionResources
from starknet_py.net.schemas.common import Felt, PriceUnitField
from starknet_py.utils.schema import Schema


class ExecutionResourcesSchema(Schema):
    l1_gas = fields.Integer(data_key="l1_gas", required=True)
    l1_data_gas = fields.Integer(data_key="l1_data_gas", required=True)
    l2_gas = fields.Integer(data_key="l2_gas", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ExecutionResources:
        return ExecutionResources(**data)


class EstimatedFeeSchema(Schema):
    l1_gas_consumed = Felt(data_key="l1_gas_consumed", required=True)
    l1_gas_price = Felt(data_key="l1_gas_price", required=True)
    l2_gas_consumed = Felt(data_key="l2_gas_consumed", required=True)
    l2_gas_price = Felt(data_key="l2_gas_price", required=True)
    l1_data_gas_consumed = Felt(data_key="l1_data_gas_consumed", required=True)
    l1_data_gas_price = Felt(data_key="l1_data_gas_price", required=True)
    overall_fee = Felt(data_key="overall_fee", required=True)
    unit = PriceUnitField(data_key="unit", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EstimatedFee:
        return EstimatedFee(**data)
