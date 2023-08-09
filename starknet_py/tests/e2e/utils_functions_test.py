from starknet_py.net.full_node_client import _is_valid_eth_address
from starknet_py.net.schemas.common import _pascal_to_screaming_upper


def test_pascal_to_screaming_upper_valid():
    valid_names = [
        "NOT_RECEIVED",
        "RECEIVED",
        "ACCEPTED_ON_L2",
        "ACCEPTED_ON_L1",
        "REJECTED",
        "REVERTED",
        "SUCCEEDED",
    ]
    for valid in valid_names:
        assert _pascal_to_screaming_upper(valid) == valid


def test_pascal_to_screaming_upper_invalid():
    invalid_names = [
        ("NotReceived", "NOT_RECEIVED"),
        ("Received", "RECEIVED"),
        (
            "AcceptedOnL2",
            "ACCEPTED_ON_L2",
        ),
        (
            "AcceptedOnL1",
            "ACCEPTED_ON_L1",
        ),
        ("Rejected", "REJECTED"),
        ("Reverted", "REVERTED"),
        ("Succeeded", "SUCCEEDED"),
    ]
    for invalid, valid in invalid_names:
        assert _pascal_to_screaming_upper(invalid) == valid


def test_is_valid_eth_address():
    assert _is_valid_eth_address("0x333333f332a06ECB5D20D35da44ba07986D6E203")
    assert not _is_valid_eth_address("0x1")
    assert not _is_valid_eth_address("123")
