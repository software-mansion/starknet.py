import pytest

from starknet_py.net.networks import TESTNET


@pytest.mark.asyncio
async def test_full_node_client(rpc_client, map_contract):
    # pylint: disable=import-outside-toplevel, unused-variable
    # add to docs: start
    from starknet_py.net.full_node_client import FullNodeClient

    node_url = "https://your.node.url"
    full_node_client = FullNodeClient(node_url=node_url, net=TESTNET)
    # add to docs: end

    await map_contract.functions["put"].prepare(key=10, value=10).invoke(
        max_fee=int(1e20)
    )

    full_node_client = rpc_client
    # add to docs: start

    call_result = await full_node_client.get_block(block_number=0)
    # add to docs: end
