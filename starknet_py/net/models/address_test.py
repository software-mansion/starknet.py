import pytest

from starknet_py.net.models.address import compute_address, parse_address


@pytest.mark.parametrize(
    "input_addr, output",
    [(123, 123), ("859", 2137), ("0x859", 2137)],
)
def test_parse_address(input_addr, output):
    assert parse_address(input_addr) == output


def test_parse_invalid_address():
    with pytest.raises(TypeError, match="address format"):
        # Ignore typing, because it is an error check (float can't be passed here)
        # noinspection PyTypeChecker
        parse_address(0.22)  # pyright: ignore


def test_compute_address():
    assert (
        compute_address(
            class_hash=951442054899045155353616354734460058868858519055082696003992725251069061570,
            constructor_calldata=[21, 37],
            salt=1111,
        )
        == 1357105550695717639826158786311415599375114169232402161465584707209611368775
    )


def test_compute_address_with_deployer_address():
    assert (
        compute_address(
            class_hash=951442054899045155353616354734460058868858519055082696003992725251069061570,
            constructor_calldata=[21, 37],
            salt=1111,
            deployer_address=1234,
        )
        == 3179899882984850239687045389724311807765146621017486664543269641150383510696
    )
