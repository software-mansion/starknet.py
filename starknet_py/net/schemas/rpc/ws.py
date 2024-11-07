from marshmallow import Schema, fields, post_load

from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.block import BlockHeaderSchema
from starknet_py.net.schemas.rpc.event import EmittedEventSchema
from starknet_py.net.ws_full_node_client_models import (
    EventsNotification,
    NewHeadsNotification,
    NewTransactionStatus,
    PendingTransactionsNotification,
    ReorgData,
    ReorgNotification,
    SubscribeResponse,
    TransactionStatusNotification,
    UnsubscribeResponse,
)


class SubscribeResponseSchema(Schema):
    subscription_id = fields.Integer(data_key="subscription_id", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> SubscribeResponse:
        return SubscribeResponse(**data)


class NewHeadsNotificationSchema(Schema):
    subscription_id = fields.Integer(data_key="subscription_id", required=True)
    result = fields.Nested(BlockHeaderSchema(), data_key="result", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> NewHeadsNotification:
        return NewHeadsNotification(**data)


class EventsNotificationSchema(Schema):
    subscription_id = fields.Integer(data_key="subscription_id", required=True)
    result = fields.Nested(EmittedEventSchema(), data_key="result", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> EventsNotification:
        return EventsNotification(**data)


class NewTransactionStatusSchema(Schema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)
    status = fields.Dict(data_key="status", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> NewTransactionStatus:
        return NewTransactionStatus(**data)


class TransactionStatusNotificationSchema(Schema):
    subscription_id = fields.Integer(data_key="subscription_id", required=True)
    result = fields.Nested(
        NewTransactionStatusSchema(), data_key="result", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionStatusNotification:
        return TransactionStatusNotification(**data)


class PendingTransactionsNotificationSchema(Schema):
    subscription_id = fields.Integer(data_key="subscription_id", required=True)
    result = fields.Dict(data_key="result", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> PendingTransactionsNotification:
        return PendingTransactionsNotification(**data)


class UnsubscribeResponseSchema(Schema):
    result = fields.Boolean(data_key="result", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> UnsubscribeResponse:
        return UnsubscribeResponse(**data)


class ReorgDataSchema(Schema):
    starting_block_hash = Felt(data_key="starting_block_hash", required=True)
    starting_block_number = fields.Integer(
        data_key="starting_block_number", required=True, validate=lambda x: x >= 0
    )
    ending_block_hash = Felt(data_key="ending_block_hash", required=True)
    ending_block_number = fields.Integer(
        data_key="ending_block_number", required=True, validate=lambda x: x >= 0
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> ReorgData:
        return ReorgData(**data)


class ReorgNotificationSchema(Schema):
    subscription_id = fields.Integer(data_key="subscription_id", required=True)
    result = fields.Nested(ReorgDataSchema(), data_key="result", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ReorgNotification:
        return ReorgNotification(**data)
