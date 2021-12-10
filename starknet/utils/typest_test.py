import pytest

from starknet.utils.types import KeyedTuple


@pytest.mark.parametrize(
    "input_dict, expected",
    [({}, ()), ({"": 21}, (21,)), ({"key1": "value1", "2": "2"}, ("value1", "2"))],
)
def test_keyed_tuple(input_dict, expected):
    k_tuple = KeyedTuple(input_dict)

    assert k_tuple == expected
    assert k_tuple.as_dict() == input_dict
    for key, value in input_dict.items():
        assert k_tuple[key] == value


def test_invalid_arg():
    with pytest.raises(ValueError) as excinfo:
        KeyedTuple({1: "value"})

    assert "string keys are allowed" in str(excinfo.value)
