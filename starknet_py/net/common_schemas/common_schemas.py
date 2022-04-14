from typing import Any, Union, Mapping

from marshmallow import fields, ValidationError

from starknet_py.net.client_models import TransactionStatus, BlockStatus


class Felt(fields.Field):
    # TODO test that serialization and deserialization is correct
    """
    Field that serializes int to felt (hex encoded string)
    """

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        if value is None:
            return None
        return str(hex(value))

    def _deserialize(
        self,
        value: Any,
        attr: Union[str, None],
        data: Union[Mapping[str, Any], None],
        **kwargs,
    ):
        try:
            assert isinstance(value, str) and value.startswith("0x")
            return int(value, 16)
        except (ValueError, AssertionError) as error:
            raise ValidationError("Invalid felt") from error


class StatusField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        # TODO should we serialize to string?
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Union[str, None],
        data: Union[Mapping[str, Any], None],
        **kwargs,
    ):
        # TODO maybe simplify
        enum_values = {v.name: k for k, v in enumerate(TransactionStatus)}

        if value not in enum_values:
            return TransactionStatus.UNKNOWN

        return TransactionStatus(enum_values[value])


class BlockStatusField(fields.Field):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        # TODO should we serialize to string?
        return value.name if value is not None else ""

    def _deserialize(
        self,
        value: Any,
        attr: Union[str, None],
        data: Union[Mapping[str, Any], None],
        **kwargs,
    ):
        # TODO maybe simplify
        enum_values = {v.name: k for k, v in enumerate(BlockStatus)}

        if value not in enum_values:
            raise ValidationError("Invalid BlockStatus enum key")

        return BlockStatus(enum_values[value])
