import pytest

from starknet_py.constants import FIELD_PRIME
from starknet_py.serialization import FeltSerializer
from starknet_py.serialization.data_serializers.non_zero_serializer import (
    NonZeroSerializer,
)
from starknet_py.serialization.data_serializers.uint_serializer import UintSerializer


@pytest.mark.parametrize(
    "serializer, value, serialized_value",
    [
        (NonZeroSerializer(UintSerializer(128)), 123, [123]),
        (NonZeroSerializer(UintSerializer(256)), 1, [1, 0]),
        (NonZeroSerializer(FeltSerializer()), 10, [10]),
        (NonZeroSerializer(FeltSerializer()), FIELD_PRIME - 1, [FIELD_PRIME - 1]),
    ],
)
def test_valid_values(serializer, value, serialized_value):
    deserialized = serializer.deserialize(serialized_value)
    assert deserialized == value

    serialized = serializer.serialize(value)
    assert serialized == serialized_value


@pytest.mark.parametrize(
    "serializer, value, serialized_value",
    [
        (NonZeroSerializer(UintSerializer(128)), 0, [0]),
        (NonZeroSerializer(UintSerializer(256)), 0, [0, 0]),
        (NonZeroSerializer(FeltSerializer()), 0, [0]),
    ],
)
def test_invalid_values(serializer, value, serialized_value):
    with pytest.raises(ValueError, match="expected value to be non-zero"):
        serializer.deserialize(serialized_value)
        serializer.serialize(value)
