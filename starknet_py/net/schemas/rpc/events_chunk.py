from marshmallow import fields, post_load

from starknet_py.net.client_models import EventsChunk
from starknet_py.net.schemas.rpc.emitted_event import EmittedEventSchema
from starknet_py.utils.schema import Schema


class EventsChunkSchema(Schema):
    events = fields.List(
        fields.Nested(EmittedEventSchema()),
        data_key="events",
        required=True,
    )
    continuation_token = fields.String(data_key="continuation_token", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs):
        return EventsChunk(**data)
