import pytest

from starknet_py.net.models.deployer_addresses import deployer_address_from_network


@pytest.mark.parametrize("net, address", [("mainnet", 123), ("testnet", 456)])
def test_deployer_address_for_real_networks(net, address):
    res = deployer_address_from_network(net=net)

    assert res == address


@pytest.mark.parametrize("net", ["someNet.com", "otherNet.com"])
def test_throws_when_deployer_not_specified_for_custom_network(net):
    with pytest.raises(ValueError) as err:
        deployer_address_from_network(net=net)

    assert "deployer_address is required when not using predefined networks" in str(
        err.value
    )


@pytest.mark.parametrize(
    "net, deployer_address", [("someNet.com", 21), ("otherNet.com", 37)]
)
def test_deployer_address_for_custom_network(net, deployer_address):
    res = deployer_address_from_network(net=net, deployer_address=deployer_address)

    assert res == deployer_address
