# pylint: disable=unused-variable, invalid-name
import pytest

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.networks import TESTNET


def test_init():
    # docs: init_start
    gateway_client = GatewayClient(net=TESTNET)
    # or (for custom urls)
    gateway_client = GatewayClient(
        net={"feeder_gateway_url": "some_feeder_url", "gateway_url": "some_gateway_url"}
    )
    # docs: init_end


@pytest.mark.asyncio
async def test_get_block(gateway_client):
    # docs: get_block_start
    block = await gateway_client.get_block(block_hash="latest")
    # or
    block = await gateway_client.get_block(block_number=1)
    # docs: get_block_end


@pytest.mark.asyncio
async def test_get_block_traces(gateway_client):
    # docs: get_block_traces_start
    block_traces = await gateway_client.get_block_traces(block_hash="latest")
    # or
    block_traces = await gateway_client.get_block_traces(block_number=1)
    # docs: get_block_traces_end
