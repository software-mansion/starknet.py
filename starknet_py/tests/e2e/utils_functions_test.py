import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net.full_node_client import _is_valid_eth_address
from starknet_py.net.models.chains import (
    StarknetChainId,
    default_token_address_for_chain,
)


def test_is_valid_eth_address():
    assert _is_valid_eth_address("0x333333f332a06ECB5D20D35da44ba07986D6E203")
    assert not _is_valid_eth_address("0x1")
    assert not _is_valid_eth_address("123")


def test_default_token_address_for_network():
    res = default_token_address_for_chain(StarknetChainId.MAINNET)
    assert res == FEE_CONTRACT_ADDRESS

    res = default_token_address_for_chain(StarknetChainId.GOERLI)
    assert res == FEE_CONTRACT_ADDRESS

    with pytest.raises(
        ValueError,
        match="Argument token_address must be specified when using a custom network.",
    ):
        _ = default_token_address_for_chain("")  # type: ignore
