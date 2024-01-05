import re
from typing import Any, Mapping, Optional, Union

from marshmallow import Schema, ValidationError, fields, post_load

from starknet_py.net.client_models import (
    BlockStatus,
    CallType,
    DAMode,
    EntryPointType,
    PriceUnit,
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


class Uint64(fields.Field):
    """
    Field that serializes int to RPC u64 (hex encoded string)
    """

    MAX_VALUE = 2**64
    REGEX_PATTERN = r"^0x(0|[a-fA-F1-9]{1}[a-fA-F0-9]{0,15})"

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        if self._is_int_and_in_range(value):
            return hex(value)

        if self._is_str_and_valid_pattern(value):
            return value

        raise ValidationError(
            f"Invalid value provided for {self.__class__.__name__}: {value}"
        )

    def _deserialize(
        self,
        value: Any,
        attr: Union[str, None],
        data: Union[Mapping[str, Any], None],
        **kwargs,
    ):
        if self._is_int_and_in_range(value):
            return value

        if self._is_str_and_valid_pattern(value):
            return int(value, 16)

        raise ValidationError(
            f"Invalid value provided for {self.__class__.__name__}: {value}"
        )

    def _is_int_and_in_range(self, value: Any) -> bool:
        return isinstance(value, int) and 0 <= value < self.MAX_VALUE

    def _is_str_and_valid_pattern(self, value: Any) -> bool:
        return (
            isinstance(value, str)
            and re.fullmatch(self.REGEX_PATTERN, value) is not None
        )


class Uint128(Uint64):
    """
    Field that serializes int to RPC u128 (hex encoded string)
    """

    MAX_VALUE = 2**128
    REGEX_PATTERN = r"^0x(0|[a-fA-F1-9]{1}[a-fA-F0-9]{0,31})"


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


class EntryPointTypeField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ) -> EntryPointType:
        values = [v.value for v in EntryPointType]

        if value not in values:
            raise ValidationError(
                f"Invalid value provided for EntryPointType: {value}."
            )

        return EntryPointType(value)


class CallTypeField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ) -> CallType:
        values = [v.value for v in CallType]

        if value not in values:
            raise ValidationError(f"Invalid value provided for CallType: {value}.")

        return CallType(value)


class PriceUnitField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ) -> PriceUnit:
        values = [v.value for v in PriceUnit]

        if value not in values:
            raise ValidationError(f"Invalid value provided for PriceUnit: {value}.")

        return PriceUnit(value)


class DAModeField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Optional[str],
        data: Optional[Mapping[str, Any]],
        **kwargs,
    ) -> DAMode:
        names = [v.name for v in DAMode]

        if value not in names:
            raise ValidationError(f"Invalid value provided for DAMode: {value}.")

        return DAMode[value]


class StorageEntrySchema(Schema):
    key = Felt(data_key="key", required=True)
    value = Felt(data_key="value", required=True)

    @post_load
    def make_dataclass(self, data, **kwargs):
        # pylint: disable=no-self-use
        return StorageEntry(**data)
