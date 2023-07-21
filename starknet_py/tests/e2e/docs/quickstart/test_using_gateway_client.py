import pytest


@pytest.mark.asyncio
async def test_using_gateway_client():
    # pylint: disable=import-outside-toplevel, unused-variable
    # docs: start
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.net.networks import MAINNET, TESTNET

    # Use testnet for playing with Starknet
    testnet_client = GatewayClient(TESTNET)
    # or
    testnet_client = GatewayClient("testnet")

    mainnet_client = GatewayClient(MAINNET)
    # or
    mainnet_client = GatewayClient("mainnet")

    # Local network
    local_network_client = GatewayClient("http://localhost:5000")

    call_result = await testnet_client.get_block(
        "0x495c670c53e4e76d08292524299de3ba078348d861dd7b2c7cc4933dbc27943"
    )
    # docs: end
