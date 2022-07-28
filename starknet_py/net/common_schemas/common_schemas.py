from typing import Any, Union, Mapping, Optional

from marshmallow import fields, ValidationError

from starknet_py.net.client_models import (
    TransactionStatus,
    BlockStatus,
    TransactionType,
)

# pylint: disable=unused-argument


class Felt(fields.Field):
    """
    Field that serializes int to felt (hex encoded string)
    """

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return hex(value)

    def _deserialize(
        self,
        value: Any,
        attr: Union[str, None],
        data: Union[Mapping[str, Any], None],
        **kwargs,
    ):
        if not isinstance(value, str) or not value.startswith("0x"):
            raise ValidationError(f"Invalid value provided for felt: {value}")

        try:
            return int(value, 16)
        except ValueError as error:
            raise ValidationError("Invalid felt") from error


class NonPrefixedHex(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return hex(value).lstrip("0x")

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ):
        return int(value, 16)


class StatusField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ) -> TransactionStatus:
        values = [v.value for v in TransactionStatus]

        if value not in values:
            raise ValidationError(
                f"Invalid value provided for TransactionStatus: {value}"
            )

        return TransactionStatus(value)


class BlockStatusField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ) -> BlockStatus:
        values = [v.value for v in BlockStatus]

        if value in ("ABORTED", "REVERTED"):
            return BlockStatus.REJECTED

        if value not in values:
            raise ValidationError(f"Invalid value for BlockStatus provided: {value}")

        return BlockStatus(value)


class TransactionTypeField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ) -> TransactionType:
        values = [v.value for v in TransactionType]

        if value == "INVOKE_FUNCTION":
            value = "INVOKE"

        if value not in values:
            raise ValidationError(
                f"Invalid value provided for TransactionType: {value}"
            )

        return TransactionType(value)
