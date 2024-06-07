from marshmallow import post_load

from starknet_py.net.client_models import FeePayment
from starknet_py.net.schemas.common import Felt, PriceUnitField
from starknet_py.utils.schema import Schema


class FeePaymentSchema(Schema):
    amount = Felt(data_key="amount", required=True)
    unit = PriceUnitField(data_key="unit", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> FeePayment:
        return FeePayment(**data)
