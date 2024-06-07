from marshmallow import fields, post_load

from starknet_py.net.client_models import Event
from starknet_py.net.schemas.common import Felt
from starknet_py.utils.schema import Schema


class EventSchema(Schema):
    from_address = Felt(data_key="from_address", required=True)
    keys = fields.List(Felt(), data_key="keys", required=True)
    data = fields.List(Felt(), data_key="data", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Event:
        return Event(**data)
