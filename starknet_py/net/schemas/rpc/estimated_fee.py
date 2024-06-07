from marshmallow import post_load

from starknet_py.net.client_models import EstimatedFee
from starknet_py.net.schemas.common import Felt, PriceUnitField
from starknet_py.utils.schema import Schema


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
