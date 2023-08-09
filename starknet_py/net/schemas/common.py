import re
from typing import Any, Mapping, Optional, Union

from marshmallow import Schema, ValidationError, fields, post_load

from starknet_py.net.client_models import (
    BlockStatus,
    StorageEntry,
    TransactionExecutionStatus,
    TransactionFinalityStatus,
    TransactionStatus,
    TransactionType,
)

# pylint: disable=unused-argument


def _pascal_to_screaming_upper(checked_string: str) -> str:
    if bool(re.fullmatch(r"[A-Z0-9]+(?:_[A-Z0-9]+)*", checked_string)):
        return checked_string
    return re.sub(r"(?<!^)(?=[A-Z])", "_", checked_string).upper()


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
        if isinstance(value, int):
            return value

        if not isinstance(value, str) or not value.startswith("0x"):
            raise ValidationError(f"Invalid value provided for felt: {value}.")

        try:
            return int(value, 16)
        except ValueError as error:
            raise ValidationError("Invalid felt.") from error


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

        # TODO (#1143): change case insensitivity in a proper release
        assert isinstance(value, str)
        value = _pascal_to_screaming_upper(value)
        if value not in values:
            raise ValidationError(
                f"Invalid value provided for TransactionStatus: {value}."
            )

        return TransactionStatus(value)


class ExecutionStatusField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ) -> TransactionExecutionStatus:
        values = [v.value for v in TransactionExecutionStatus]

        # TODO (#1143): change case insensitivity in a proper release
        assert isinstance(value, str)
        value = _pascal_to_screaming_upper(value)
        if value not in values:
            raise ValidationError(
                f"Invalid value provided for TransactionExecutionStatus: {value}."
            )

        return TransactionExecutionStatus(value)


class FinalityStatusField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ) -> TransactionFinalityStatus:
        values = [v.value for v in TransactionFinalityStatus]

        # TODO (#1143): change case insensitivity in a proper release
        assert isinstance(value, str)
        value = _pascal_to_screaming_upper(value)
        if value not in values:
            raise ValidationError(
                f"Invalid value provided for TransactionFinalityStatus: {value}."
            )

        return TransactionFinalityStatus(value)


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
            raise ValidationError(f"Invalid value for BlockStatus provided: {value}.")

        return BlockStatus(value)


class TransactionTypeField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        if value == TransactionType.INVOKE:
            return "INVOKE_FUNCTION"
        return value.name

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
                f"Invalid value provided for TransactionType: {value}."
            )

        return TransactionType(value)


class StorageEntrySchema(Schema):
    key = Felt(data_key="key", required=True)
    value = Felt(data_key="value", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        # pylint: disable=no-self-use
        return StorageEntry(**data)
