from marshmallow import fields, post_load

from starknet_py.net.client_models import EmittedEvent
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.event import EventSchema


class EmittedEventSchema(EventSchema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)
    block_hash = Felt(data_key="block_hash", load_default=None)
    block_number = fields.Integer(data_key="block_number", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EmittedEvent:
        return EmittedEvent(**data)
