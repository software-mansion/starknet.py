import pytest

from starknet_py.net.networks import TESTNET
from starknet_py.tests.e2e.utils import DevnetClientFactory


@pytest.mark.asyncio
async def test_full_node_client(run_devnet):
    # pylint: disable=import-outside-toplevel, unused-variable
    # add to docs: start
    from starknet_py.net.full_node_client import FullNodeClient

    node_url = "https://your.node.url"
    full_node_client = FullNodeClient(node_url=node_url, net=TESTNET)
    # add to docs: end

    full_node_client = DevnetClientFactory(run_devnet).make_rpc_client()
    node_url = run_devnet
    # add to docs: start

    call_result = await full_node_client.get_block(block_number=1)
    # add to docs: end
