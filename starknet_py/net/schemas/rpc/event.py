from marshmallow import fields, post_load, validate

from starknet_py.net.client_models import (
    EmittedEvent,
    EmittedEventWithFinalityStatus,
    Event,
    EventsChunk,
)
from starknet_py.net.schemas.common import Felt, FinalityStatusField
from starknet_py.utils.schema import Schema


class EventSchema(Schema):
    from_address = Felt(data_key="from_address", required=True)
    keys = fields.List(Felt(), data_key="keys", required=True)
    data = fields.List(Felt(), data_key="data", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> Event:
        return Event(**data)


class EmittedEventSchema(EventSchema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)
    transaction_index = fields.Integer(
        data_key="transaction_index",
        required=True,
        validate=validate.Range(min=0, error="`transaction_index` must be >= 0"),
    )
    event_index = fields.Integer(
        data_key="event_index",
        required=True,
        validate=validate.Range(min=0, error="`event_index` must be >= 0"),
    )
    block_hash = Felt(data_key="block_hash", load_default=None)
    block_number = fields.Integer(data_key="block_number", load_default=None)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EmittedEvent:
        return EmittedEvent(**data)


class EmittedEventWithFinalitySchema(EmittedEventSchema):
    finality_status = FinalityStatusField(data_key="finality_status", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EmittedEventWithFinalityStatus:
        return EmittedEventWithFinalityStatus(**data)


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
