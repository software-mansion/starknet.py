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
        (123 + 456 * SHIFT_128 + 789 * SHIFT_256 + 101112 * SHIFT_384, [123, 456, 789, 101112]),
        (
            21323213211421424142 + 347932774343 * SHIFT_128 + 123456789 * SHIFT_256 + 987654321 * SHIFT_384,
            [21323213211421424142, 347932774343, 123456789, 987654321],
        ),
        (0, [0, 0, 0, 0]),
        (MAX_U128, [MAX_U128, 0, 0, 0]),
        (MAX_U128 * SHIFT_128, [0, MAX_U128, 0, 0]),
        (MAX_U128 * SHIFT_256, [0, 0, MAX_U128, 0]),
        (MAX_U128 * SHIFT_384, [0, 0, 0, MAX_U128]),
        (MAX_U128 + MAX_U128 * SHIFT_128 + MAX_U128 * SHIFT_256 + MAX_U128 * SHIFT_384, [MAX_U128, MAX_U128, MAX_U128, MAX_U128]),
    ],
)
def test_valid_values(value, serialized_value):
    deserialized = serializer.deserialize(serialized_value)
    assert deserialized == value

    serialized = serializer.serialize(value)
    assert serialized == serialized_value

    assert serialized_value == serializer.serialize(
        {"d0": serialized_value[0], "d1": serialized_value[1], "d2": serialized_value[2], "d3": serialized_value[3]}
    )


def test_deserialize_invalid_values():
    # We need to escape braces
    d0_error_message = re.escape(
        "Error at path 'd0': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=d0_error_message):
        serializer.deserialize([MAX_U128 + 1, 0, 0, 0])
    with pytest.raises(InvalidValueException, match=d0_error_message):
        serializer.deserialize([MAX_U128 + 1, MAX_U128 + 1, MAX_U128 + 1, MAX_U128 + 1])
    with pytest.raises(InvalidValueException, match=d0_error_message):
        serializer.deserialize([-1, 0, 0, 0])

    d1_error_message = re.escape(
        "Error at path 'd1': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=d1_error_message):
        serializer.deserialize([0, MAX_U128 + 1, 0, 0])
    with pytest.raises(InvalidValueException, match=d1_error_message):
        serializer.deserialize([0, -1, 0, 0])

    d2_error_message = re.escape(
        "Error at path 'd2': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=d2_error_message):
        serializer.deserialize([0, 0, MAX_U128 + 1, 0])
    with pytest.raises(InvalidValueException, match=d2_error_message):
        serializer.deserialize([0, 0, -1, 0])

    d3_error_message = re.escape(
        "Error at path 'd3': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=d3_error_message):
        serializer.deserialize([0, 0, 0, MAX_U128 + 1])
    with pytest.raises(InvalidValueException, match=d3_error_message):
        serializer.deserialize([0, 0, 0, -1])


def test_serialize_invalid_int_value():
    error_message = re.escape("Error: Uint512 is expected to be in range [0;2**512)")
    with pytest.raises(InvalidValueException, match=error_message):
        serializer.serialize(2**512)
    with pytest.raises(InvalidValueException, match=error_message):
        serializer.serialize(-1)


def test_serialize_invalid_dict_values():
    d0_error_message = re.escape(
        "Error at path 'd0': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=d0_error_message):
        serializer.serialize({"d0": -1, "d1": 12324, "d2": 456, "d3": 789})
    with pytest.raises(InvalidValueException, match=d0_error_message):
        serializer.serialize({"d0": MAX_U128 + 1, "d1": 4543535, "d2": 456, "d3": 789})

    d1_error_message = re.escape(
        "Error at path 'd1': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=d1_error_message):
        serializer.serialize({"d0": 652432, "d1": -1, "d2": 456, "d3": 789})
    with pytest.raises(InvalidValueException, match=d1_error_message):
        serializer.serialize({"d0": 0, "d1": MAX_U128 + 1, "d2": 456, "d3": 789})

    d2_error_message = re.escape(
        "Error at path 'd2': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=d2_error_message):
        serializer.serialize({"d0": 652432, "d1": 123, "d2": -1, "d3": 789})
    with pytest.raises(InvalidValueException, match=d2_error_message):
        serializer.serialize({"d0": 0, "d1": 123, "d2": MAX_U128 + 1, "d3": 789})

    d3_error_message = re.escape(
        "Error at path 'd3': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=d3_error_message):
        serializer.serialize({"d0": 652432, "d1": 123, "d2": 456, "d3": -1})
    with pytest.raises(InvalidValueException, match=d3_error_message):
        serializer.serialize({"d0": 0, "d1": 123, "d2": 456, "d3": MAX_U128 + 1})


def test_invalid_type():
    error_message = re.escape(
        "Error: expected int or dict, received 'wololoo' of type '<class 'str'>'."
    )
    with pytest.raises(InvalidTypeException, match=error_message):
        serializer.serialize("wololoo")  # type: ignore