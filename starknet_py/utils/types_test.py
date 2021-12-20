import pytest
from starkware.crypto.signature.signature import FIELD_PRIME

from starknet_py.utils.types import parse_address, cairo_vm_range_check


@pytest.mark.parametrize(
    "input_addr, output",
    [(123, 123), ("859", 2137), ("0x859", 2137)],
)
def test_parse_address(input_addr, output):
    assert parse_address(input_addr) == output


def test_parse_invalid_address():
    with pytest.raises(TypeError) as excinfo:
        parse_address(0.22)

    assert "address format" in str(excinfo.value)


@pytest.mark.parametrize("value", [-1, FIELD_PRIME, FIELD_PRIME + 1, -FIELD_PRIME])
def test_invalid_cairo_vm_values(value):
    with pytest.raises(ValueError) as v_err:
        cairo_vm_range_check(value)

    assert "is expected to be in range [0;" in str(v_err.value)


@pytest.mark.parametrize("value", [0, 1, FIELD_PRIME - 1])
def cairo_vm_range_check_good_numbers(value):
    cairo_vm_range_check(value)
