from marshmallow import post_load

from starknet_py.net.client_models import ResourceBounds
from starknet_py.net.schemas.common import Uint64, Uint128
from starknet_py.utils.schema import Schema


class ResourceBoundsSchema(Schema):
    max_amount = Uint64(data_key="max_amount", required=True)
    max_price_per_unit = Uint128(data_key="max_price_per_unit", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ResourceBounds:
        return ResourceBounds(**data)
