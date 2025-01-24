from marshmallow import fields, post_load

from starknet_py.net.client_models import EstimatedFee, ExecutionResources
from starknet_py.net.schemas.common import Felt, PriceUnitField
from starknet_py.utils.schema import Schema


class ExecutionResourcesSchema(Schema):
    l1_gas = fields.Integer(data_key="l1_gas", required=True)
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
        # data = {
        #     "l1_gas_consumed": 0x186A0,
        #     "l1_data_gas_consumed": 0x1,
        #     "l1_gas_price": 0x174876E800,
        #     "l1_data_gas_price": 0x174876E800,
        #     "l2_gas_consumed": 0x0,
        #     "l2_gas_price": 0x0,
        #     "overall_fee": 10000100000000000,
        #     "unit": "FRI",
        # }
        return EstimatedFee(**data)
