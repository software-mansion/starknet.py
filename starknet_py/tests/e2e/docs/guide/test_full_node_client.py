import pytest

from starknet_py.contract import Contract
from starknet_py.net.networks import TESTNET
from starknet_py.tests.e2e.account.account_client_test import map_source_code


@pytest.mark.asyncio
async def test_full_node_client(rpc_client, account_client):
    # pylint: disable=import-outside-toplevel, unused-variable
    # add to docs: start
    from starknet_py.net.full_node_client import FullNodeClient

    node_url = "https://your.node.url"
    full_node_client = FullNodeClient(node_url=node_url, net=TESTNET)
    # add to docs: end

    deployment_result = await Contract.deploy(
        client=account_client, compilation_source=map_source_code
    )
    await deployment_result.wait_for_acceptance()

    full_node_client = rpc_client
    # add to docs: start

    call_result = await full_node_client.get_block(block_number=0)
    # add to docs: end
