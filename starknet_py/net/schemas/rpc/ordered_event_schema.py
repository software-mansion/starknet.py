from marshmallow import fields, post_load

from starknet_py.net.client_models import OrderedEvent
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class OrderedEventSchema(Schema):
    keys = fields.List(Felt(), data_key="keys", required=True)
    data = fields.List(Felt(), data_key="data", required=True)
    order = fields.Integer(data_key="order", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return OrderedEvent(**data)
