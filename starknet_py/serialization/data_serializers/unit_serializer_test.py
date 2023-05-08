import re

import pytest

from starknet_py.serialization.data_serializers.unit_serializer import UnitSerializer

serializer = UnitSerializer()


def test_deserialize_unit():
    deserialized = serializer.deserialize([])

    assert deserialized is None


def test_throws_when_serialize_unit():
    error_message = re.escape("Unit can't be serialized.")

    with pytest.raises(ValueError, match=error_message):
        serializer.serialize(None)
