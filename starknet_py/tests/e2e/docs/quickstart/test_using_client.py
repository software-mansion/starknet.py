import pytest


@pytest.mark.asyncio
async def test_using_client():
    # pylint: disable=import-outside-toplevel, unused-variable
    # add to docs: start
    from starknet_py.net import Client
    from starknet_py.net.networks import TESTNET, MAINNET

    # Use testnet for playing with Starknet
    testnet_client = Client(TESTNET)
    # or
    testnet_client = Client("testnet")

    mainnet_client = Client(MAINNET)
    # or
    mainnet_client = Client("mainnet")

    # Local network
    from starknet_py.net.models import StarknetChainId

    local_network_client = Client(
        "http://localhost:5000", chain=StarknetChainId.TESTNET
    )

    call_result = await testnet_client.get_block(
        "0x495c670c53e4e76d08292524299de3ba078348d861dd7b2c7cc4933dbc27943"
    )
    # add to docs: end
