import pytest

from starknet_py.net.models.chains import StarknetChainId, chain_from_network
from starknet_py.net.networks import CustomGatewayUrls


@pytest.mark.parametrize(
    "net",
    ["custom_url", CustomGatewayUrls(feeder_gateway_url="abc", gateway_url="def")],
)
def test_unknown_network(net):
    with pytest.raises(ValueError, match="Unknown Network."):
        StarknetChainId.from_network(net=net)


def test_no_chain_for_custom_network():
    with pytest.raises(
        ValueError, match="Chain is required when not using predefined networks."
    ):
        chain_from_network("some_custom_url")
