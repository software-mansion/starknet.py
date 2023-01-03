import pytest
from marshmallow import Schema, ValidationError

from starknet_py.net.client_models import BlockStatus, TransactionStatus
from starknet_py.net.schemas.common import NonPrefixedHex
from starknet_py.net.schemas.rpc import BlockStatusField, Felt, StatusField


def test_serialize_felt():
    class SchemaWithFelt(Schema):
        value1 = Felt(data_key="value1")

    data = {"value1": 2137}

    serialized = SchemaWithFelt().dumps(data)
    assert '"value1": "0x859"' in serialized


def test_serialize_felt_throws_on_none():
    class SchemaWithFelt(Schema):
        value1 = Felt(data_key="value1")

    data = {"value1": None}
    with pytest.raises(TypeError):
        SchemaWithFelt().dumps(data)


def test_deserialize_felt():
    class SchemaWithFelt(Schema):
        value1 = Felt(data_key="value1")

    data = {"value1": "0x859"}

    deserialized = SchemaWithFelt().load(data)
    assert isinstance(deserialized, dict)
    assert deserialized["value1"] == 2137


def test_deserialize_felt_throws_on_invalid_data():
    class SchemaWithFelt(Schema):
        value1 = Felt(data_key="value1")

    data = {"value1": "2137"}

    with pytest.raises(ValidationError, match="Invalid value provided for felt"):
        SchemaWithFelt().load(data)

    data = {"value1": "0xwww"}
    with pytest.raises(ValidationError, match="Invalid felt."):
        SchemaWithFelt().load(data)


def test_serialize_hex():
    class SchemaWithHex(Schema):
        value1 = NonPrefixedHex(data_key="value1")

    data = {"value1": 123}

    serialized = SchemaWithHex().dump(data)
    assert isinstance(serialized, dict)
    assert serialized["value1"] == "7b"


def test_deserialize_hex():
    class SchemaWithHex(Schema):
        value1 = NonPrefixedHex(data_key="value1")

    data = {"value1": "7b"}

    deserialized = SchemaWithHex().load(data)
    assert isinstance(deserialized, dict)
    assert deserialized["value1"] == 123


def test_serialize_status_field():
    class SchemaWithStatusField(Schema):
        value1 = StatusField(data_key="value1")

    data = {"value1": TransactionStatus.RECEIVED}

    serialized = SchemaWithStatusField().dumps(data)
    assert '"value1": "RECEIVED"' in serialized


def test_deserialize_status_field():
    class SchemaWithStatusField(Schema):
        value1 = StatusField(data_key="value1")

    data = {"value1": "RECEIVED"}

    deserialized = SchemaWithStatusField().load(data)
    assert isinstance(deserialized, dict)
    assert deserialized["value1"] == TransactionStatus.RECEIVED


def test_deserialize_status_field_throws_on_invalid_data():
    class SchemaWithStatusField(Schema):
        value1 = StatusField(data_key="value1")

    data = {"value1": "SENT"}

    with pytest.raises(
        ValidationError, match="Invalid value provided for TransactionStatus"
    ):
        SchemaWithStatusField().load(data)


def test_serialize_block_status_field():
    class SchemaWithBlockStatusField(Schema):
        value1 = BlockStatusField(data_key="value1")

    data = {"value1": BlockStatus.PENDING}

    serialized = SchemaWithBlockStatusField().dumps(data)
    assert '"value1": "PENDING"' in serialized


def test_deserialize_block_status_field():
    class SchemaWithBlockStatusField(Schema):
        value1 = BlockStatusField(data_key="value1")

    data = {"value1": "PENDING"}

    deserialized = SchemaWithBlockStatusField().load(data)
    assert isinstance(deserialized, dict)
    assert deserialized["value1"] == BlockStatus.PENDING


def test_serialize_block_status_field_throws_on_invalid_data():
    class SchemaWithBlockStatusField(Schema):
        value1 = BlockStatusField(data_key="value1")

    data = {"value1": "SENT"}

    with pytest.raises(ValidationError, match="Invalid value for BlockStatus provided"):
        SchemaWithBlockStatusField().load(data)
