import re

import pytest

from starknet_py.constants import FIELD_PRIME
from starknet_py.serialization.data_serializers.int_serializer import IntSerializer
from starknet_py.serialization.errors import InvalidTypeException, InvalidValueException

u128_serializer = IntSerializer(bits=128)

MIN_I128 = -(2**127)
MAX_I128 = 2**127 - 1


def _felt(x: int) -> int:
    if abs(x) >= FIELD_PRIME:
        raise ValueError("Value is out of field range.")

    return x + FIELD_PRIME if x < 0 else x


@pytest.mark.parametrize(
    "value, serializer, serialized_value",
    [
        (0, u128_serializer, [_felt(0)]),
        # positive values
        (1, u128_serializer, [_felt(1)]),
        (1000, u128_serializer, [_felt(1000)]),
        # negative values
        (-1, u128_serializer, [_felt(-1)]),
        (-1000, u128_serializer, [_felt(-1000)]),
        # boundaries
        (MIN_I128, u128_serializer, [_felt(MIN_I128)]),
        (MAX_I128, u128_serializer, [_felt(MAX_I128)]),
    ],
)
def test_valid_values(value, serializer, serialized_value):
    deserialized = serializer.deserialize(serialized_value)
    assert deserialized == value

    serialized = serializer.serialize(value)
    assert serialized == serialized_value


def test_deserialize_invalid_i128_values():
    error_message = re.escape(
        f"Error at path 'int128': expected value in range [{MIN_I128};{MAX_I128}]"
    )
    with pytest.raises(InvalidValueException, match=error_message):
        u128_serializer.deserialize([MIN_I128 - 1])
    with pytest.raises(InvalidValueException, match=error_message):
        u128_serializer.deserialize([MAX_I128 + 1])


def test_serialize_invalid_i128_value():
    error_message = re.escape(f"Error: expected value in range [{MIN_I128};{MAX_I128}]")
    with pytest.raises(InvalidValueException, match=error_message):
        u128_serializer.serialize(2**128)
    with pytest.raises(InvalidValueException, match=error_message):
        u128_serializer.serialize(-(2**128))


def test_invalid_type():
    error_message = re.escape(
        "Error: expected int, received 'wololoo' of type '<class 'str'>'."
    )
    with pytest.raises(InvalidTypeException, match=error_message):
        u128_serializer.serialize("wololoo")  # type: ignore
