import pytest

from starknet_py.net.models.address import parse_address


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
