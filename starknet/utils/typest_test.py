import pytest

from starknet.utils.types import KeyedTuple, parse_address


@pytest.mark.parametrize(
    "input, output",
    [(123, 123), ("859", 2137), ("0x859", 2137)],
)
def test_parse_address(input, output):
    assert parse_address(input) == output


def test_parse_invalid_address():
    with pytest.raises(TypeError) as excinfo:
        parse_address(0.22)

    assert "address format" in str(excinfo.value)


@pytest.mark.parametrize(
    "input_dict, expected",
    [({}, ()), ({"": 21}, (21,)), ({"key1": "value1", "2": "2"}, ("value1", "2"))],
)
def test_keyed_tuple(input_dict, expected):
    k_tuple = KeyedTuple(input_dict)

    assert k_tuple == expected
    assert k_tuple.as_dict() == input_dict

    index = 0
    for key, value in input_dict.items():
        assert k_tuple[key] == value
        assert k_tuple[index] == value

        index += 1


def test_keyed_tuple_invalid_arg():
    with pytest.raises(ValueError) as excinfo:
        KeyedTuple({1: "value"})

    assert "string keys are allowed" in str(excinfo.value)
