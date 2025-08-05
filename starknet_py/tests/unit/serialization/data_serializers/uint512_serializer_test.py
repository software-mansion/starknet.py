import re

import pytest

from starknet_py.serialization.data_serializers.uint512_serializer import (
    Uint512Serializer,
)
from starknet_py.serialization.errors import InvalidTypeException, InvalidValueException

serializer = Uint512Serializer()
SHIFT_128 = 2**128
SHIFT_256 = 2**256
SHIFT_384 = 2**384
MAX_U128 = SHIFT_128 - 1


@pytest.mark.parametrize(
    "value, serialized_value",
    [
        (123 + 456 * SHIFT_128 + 789 * SHIFT_256 + 101 * SHIFT_384, [123, 456, 789, 101]),
        (
            21323213211421424142 + 347932774343 * SHIFT_128 + 987654321 * SHIFT_256 + 123456789 * SHIFT_384,
            [21323213211421424142, 347932774343, 987654321, 123456789],
        ),
        (0, [0, 0, 0, 0]),
        (MAX_U128, [MAX_U128, 0, 0, 0]),
        (MAX_U128 * SHIFT_128, [0, MAX_U128, 0, 0]),
        (MAX_U128 * SHIFT_256, [0, 0, MAX_U128, 0]),
        (MAX_U128 * SHIFT_384, [0, 0, 0, MAX_U128]),
        (MAX_U128 + MAX_U128 * SHIFT_128 + MAX_U128 * SHIFT_256 + MAX_U128 * SHIFT_384, [MAX_U128, MAX_U128, MAX_U128, MAX_U128]),
        (1, [1, 0, 0, 0]),
        (SHIFT_128, [0, 1, 0, 0]),
        (SHIFT_256, [0, 0, 1, 0]),
        (SHIFT_384, [0, 0, 0, 1]),
    ],
)
def test_valid_values(value, serialized_value):
    deserialized = serializer.deserialize(serialized_value)
    assert deserialized == value

    serialized = serializer.serialize(value)
    assert serialized == serialized_value

    assert serialized_value == serializer.serialize(
        {"low0": serialized_value[0], "low1": serialized_value[1], "high0": serialized_value[2], "high1": serialized_value[3]}
    )


def test_deserialize_invalid_values():
    # We need to escape braces
    low0_error_message = re.escape(
        "Error at path 'low0': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=low0_error_message):
        serializer.deserialize([MAX_U128 + 1, 0, 0, 0])
    with pytest.raises(InvalidValueException, match=low0_error_message):
        serializer.deserialize([MAX_U128 + 1, MAX_U128 + 1, MAX_U128 + 1, MAX_U128 + 1])
    with pytest.raises(InvalidValueException, match=low0_error_message):
        serializer.deserialize([-1, 0, 0, 0])

    low1_error_message = re.escape(
        "Error at path 'low1': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=low1_error_message):
        serializer.deserialize([0, MAX_U128 + 1, 0, 0])
    with pytest.raises(InvalidValueException, match=low1_error_message):
        serializer.deserialize([0, -1, 0, 0])

    high0_error_message = re.escape(
        "Error at path 'high0': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=high0_error_message):
        serializer.deserialize([0, 0, MAX_U128 + 1, 0])
    with pytest.raises(InvalidValueException, match=high0_error_message):
        serializer.deserialize([0, 0, -1, 0])

    high1_error_message = re.escape(
        "Error at path 'high1': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=high1_error_message):
        serializer.deserialize([0, 0, 0, MAX_U128 + 1])
    with pytest.raises(InvalidValueException, match=high1_error_message):
        serializer.deserialize([0, 0, 0, -1])


def test_serialize_invalid_int_value():
    error_message = re.escape("Error: Uint512 is expected to be in range [0;2**512)")
    with pytest.raises(InvalidValueException, match=error_message):
        serializer.serialize(2**512)
    with pytest.raises(InvalidValueException, match=error_message):
        serializer.serialize(-1)


def test_serialize_invalid_dict_values():
    low0_error_message = re.escape(
        "Error at path 'low0': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=low0_error_message):
        serializer.serialize({"low0": -1, "low1": 12324, "high0": 456, "high1": 789})
    with pytest.raises(InvalidValueException, match=low0_error_message):
        serializer.serialize({"low0": MAX_U128 + 1, "low1": 4543535, "high0": 456, "high1": 789})

    low1_error_message = re.escape(
        "Error at path 'low1': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=low1_error_message):
        serializer.serialize({"low0": 652432, "low1": -1, "high0": 456, "high1": 789})
    with pytest.raises(InvalidValueException, match=low1_error_message):
        serializer.serialize({"low0": 0, "low1": MAX_U128 + 1, "high0": 456, "high1": 789})

    high0_error_message = re.escape(
        "Error at path 'high0': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=high0_error_message):
        serializer.serialize({"low0": 652432, "low1": 123, "high0": -1, "high1": 789})
    with pytest.raises(InvalidValueException, match=high0_error_message):
        serializer.serialize({"low0": 0, "low1": 123, "high0": MAX_U128 + 1, "high1": 789})

    high1_error_message = re.escape(
        "Error at path 'high1': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=high1_error_message):
        serializer.serialize({"low0": 652432, "low1": 123, "high0": 456, "high1": -1})
    with pytest.raises(InvalidValueException, match=high1_error_message):
        serializer.serialize({"low0": 0, "low1": 123, "high0": 456, "high1": MAX_U128 + 1})


def test_invalid_type():
    error_message = re.escape(
        "Error: expected int or dict, received 'wololoo' of type '<class 'str'>'."
    )
    with pytest.raises(InvalidTypeException, match=error_message):
        serializer.serialize("wololoo")  # type: ignore