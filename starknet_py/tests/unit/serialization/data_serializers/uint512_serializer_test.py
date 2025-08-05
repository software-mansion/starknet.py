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
        {"limb0": serialized_value[0], "limb1": serialized_value[1], "limb2": serialized_value[2], "limb3": serialized_value[3]}
    )


def test_deserialize_invalid_values():
    # We need to escape braces
    limb0_error_message = re.escape(
        "Error at path 'limb0': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=limb0_error_message):
        serializer.deserialize([MAX_U128 + 1, 0, 0, 0])
    with pytest.raises(InvalidValueException, match=limb0_error_message):
        serializer.deserialize([MAX_U128 + 1, MAX_U128 + 1, MAX_U128 + 1, MAX_U128 + 1])
    with pytest.raises(InvalidValueException, match=limb0_error_message):
        serializer.deserialize([-1, 0, 0, 0])

    limb1_error_message = re.escape(
        "Error at path 'limb1': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=limb1_error_message):
        serializer.deserialize([0, MAX_U128 + 1, 0, 0])
    with pytest.raises(InvalidValueException, match=limb1_error_message):
        serializer.deserialize([0, -1, 0, 0])

    limb2_error_message = re.escape(
        "Error at path 'limb2': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=limb2_error_message):
        serializer.deserialize([0, 0, MAX_U128 + 1, 0])
    with pytest.raises(InvalidValueException, match=limb2_error_message):
        serializer.deserialize([0, 0, -1, 0])

    limb3_error_message = re.escape(
        "Error at path 'limb3': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=limb3_error_message):
        serializer.deserialize([0, 0, 0, MAX_U128 + 1])
    with pytest.raises(InvalidValueException, match=limb3_error_message):
        serializer.deserialize([0, 0, 0, -1])


def test_serialize_invalid_int_value():
    error_message = re.escape("Error: Uint512 is expected to be in range [0;2**512)")
    with pytest.raises(InvalidValueException, match=error_message):
        serializer.serialize(2**512)
    with pytest.raises(InvalidValueException, match=error_message):
        serializer.serialize(-1)


def test_serialize_invalid_dict_values():
    limb0_error_message = re.escape(
        "Error at path 'limb0': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=limb0_error_message):
        serializer.serialize({"limb0": -1, "limb1": 12324, "limb2": 456, "limb3": 789})
    with pytest.raises(InvalidValueException, match=limb0_error_message):
        serializer.serialize({"limb0": MAX_U128 + 1, "limb1": 4543535, "limb2": 456, "limb3": 789})

    limb1_error_message = re.escape(
        "Error at path 'limb1': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=limb1_error_message):
        serializer.serialize({"limb0": 652432, "limb1": -1, "limb2": 456, "limb3": 789})
    with pytest.raises(InvalidValueException, match=limb1_error_message):
        serializer.serialize({"limb0": 0, "limb1": MAX_U128 + 1, "limb2": 456, "limb3": 789})

    limb2_error_message = re.escape(
        "Error at path 'limb2': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=limb2_error_message):
        serializer.serialize({"limb0": 652432, "limb1": 123, "limb2": -1, "limb3": 789})
    with pytest.raises(InvalidValueException, match=limb2_error_message):
        serializer.serialize({"limb0": 0, "limb1": 123, "limb2": MAX_U128 + 1, "limb3": 789})

    limb3_error_message = re.escape(
        "Error at path 'limb3': expected value in range [0;2**128)"
    )
    with pytest.raises(InvalidValueException, match=limb3_error_message):
        serializer.serialize({"limb0": 652432, "limb1": 123, "limb2": 456, "limb3": -1})
    with pytest.raises(InvalidValueException, match=limb3_error_message):
        serializer.serialize({"limb0": 0, "limb1": 123, "limb2": 456, "limb3": MAX_U128 + 1})


def test_invalid_type():
    error_message = re.escape(
        "Error: expected int or dict, received 'wololoo' of type '<class 'str'>'."
    )
    with pytest.raises(InvalidTypeException, match=error_message):
        serializer.serialize("wololoo")  # type: ignore