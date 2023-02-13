import pytest

from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import Network


@pytest.mark.asyncio
async def test_full_node_client(full_node_client, map_contract):
    # pylint: disable=import-outside-toplevel, unused-variable
    full_node_client_fixture = full_node_client

    # docs: start
    from starknet_py.net.full_node_client import FullNodeClient

    node_url = "https://your.node.url"
    full_node_client = FullNodeClient(
        net=Network(address=node_url, chain_id=StarknetChainId.TESTNET)
    )
    # docs: end

    await map_contract.functions["put"].prepare(key=10, value=10).invoke(
        max_fee=int(1e20)
    )

    full_node_client = full_node_client_fixture
    # docs: start

    call_result = await full_node_client.get_block(block_number=0)
    # docs: end
