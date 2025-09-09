from typing import Any, Optional

from marshmallow import ValidationError, fields, post_load

from starknet_py.net.client_models import Transaction
from starknet_py.net.client_utils import _to_rpc_felt
from starknet_py.net.schemas.common import Felt
from starknet_py.net.schemas.rpc.block import BlockHeaderSchema
from starknet_py.net.schemas.rpc.event import EmittedEventSchema
from starknet_py.net.schemas.rpc.transactions import (
    TransactionStatusResponseSchema,
    TypesOfTransactionsSchema,
)
from starknet_py.net.websockets.models import (
    NewEventsNotification,
    NewHeadsNotification,
    NewTransactionStatus,
    PendingTransactionsNotification,
    ReorgData,
    ReorgNotification,
    TransactionStatusNotification,
)
from starknet_py.utils.schema import Schema


class NewHeadsNotificationSchema(Schema):
    subscription_id = fields.Str(data_key="subscription_id", required=True)
    result = fields.Nested(BlockHeaderSchema(), data_key="result", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> NewHeadsNotification:
        return NewHeadsNotification(**data)


class NewEventsNotificationSchema(Schema):
    subscription_id = fields.Str(data_key="subscription_id", required=True)
    result = fields.Nested(EmittedEventSchema(), data_key="result", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> NewEventsNotification:
        return NewEventsNotification(**data)


class NewTransactionStatusSchema(Schema):
    transaction_hash = Felt(data_key="transaction_hash", required=True)
    status = fields.Nested(
        TransactionStatusResponseSchema(), data_key="status", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> NewTransactionStatus:
        return NewTransactionStatus(**data)


class TransactionStatusNotificationSchema(Schema):
    subscription_id = fields.Str(data_key="subscription_id", required=True)
    result = fields.Nested(
        NewTransactionStatusSchema(), data_key="result", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> TransactionStatusNotification:
        return TransactionStatusNotification(**data)


class PendingTransactionsNotificationResultField(fields.Field):
    def _serialize(self, value: Any, attr: Optional[str], obj: Any, **kwargs):
        if isinstance(value, int):
            return _to_rpc_felt(value)
        elif isinstance(value, Transaction):
            return TypesOfTransactionsSchema().dump(value)
        raise ValidationError(
            f"Invalid value provided for {self.__class__.__name__}: {value}"
        )

    def _deserialize(
        self,
        value,
        attr,
        data,
        **kwargs,
    ):
        if isinstance(value, str):
            return Felt().deserialize(value, attr, data, **kwargs)
        elif isinstance(value, dict):
            return TypesOfTransactionsSchema().load(value)
        raise ValidationError(
            f"Invalid value provided for {self.__class__.__name__}: {value}"
        )


class PendingTransactionsNotificationSchema(Schema):
    subscription_id = fields.Str(data_key="subscription_id", required=True)
    result = PendingTransactionsNotificationResultField(
        data_key="result", required=True
    )

    @post_load
    def make_dataclass(self, data, **kwargs) -> PendingTransactionsNotification:
        return PendingTransactionsNotification(**data)


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
    subscription_id = fields.Str(data_key="subscription_id", required=True)
    result = fields.Nested(ReorgDataSchema(), data_key="result", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs) -> ReorgNotification:
        return ReorgNotification(**data)
