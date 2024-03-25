from starknet_py.net.full_node_client import _is_valid_eth_address


def test_is_valid_eth_address():
    assert _is_valid_eth_address("0x333333f332a06ECB5D20D35da44ba07986D6E203")
    assert not _is_valid_eth_address("0x1")
    assert not _is_valid_eth_address("123")
