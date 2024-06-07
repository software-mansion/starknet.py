from marshmallow import post_load

from starknet_py.net.client_models import ResourcePrice
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class ResourcePriceSchema(Schema):
    price_in_fri = Felt(data_key="price_in_fri", required=True)
    price_in_wei = Felt(data_key="price_in_wei", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ResourcePrice:
        return ResourcePrice(**data)
