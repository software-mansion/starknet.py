import pytest

from starknet_py.net.client_models import StarknetBlock, Transaction
from starknet_py.net.networks import TESTNET


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_using_full_node_client(rpc_client):
    # pylint: disable=import-outside-toplevel, unused-variable
    # add to docs: start
    from starknet_py.net.full_node_client import FullNodeClient

    node_url = "https://your.node.url"
    full_node_client = FullNodeClient(node_url=node_url, net=TESTNET)
    # add to docs: end

    full_node_client = rpc_client
    # add to docs: start

    call_result = await full_node_client.get_block(block_number=1)
    # add to docs: end
    assert isinstance(call_result, StarknetBlock)
    assert len(call_result.transactions) == 1
    assert isinstance(call_result.transactions[0], Transaction)
    assert call_result.block_hash
