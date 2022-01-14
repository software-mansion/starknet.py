import pytest

from starknet_py.net.models.address import parse_address, compute_address


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


def test_compute_address():
    assert (
        compute_address(
            951442054899045155353616354734460058868858519055082696003992725251069061570,
            [21, 37],
            1111,
        )
        == 1357105550695717639826158786311415599375114169232402161465584707209611368775
    )
