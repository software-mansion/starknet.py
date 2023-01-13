# pylint: disable=unused-variable, invalid-name
import pytest
from starkware.starknet.public.abi import get_storage_var_address

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
    block = await gateway_client.get_block(block_number=0)
    # docs: get_block_end


@pytest.mark.asyncio
async def test_get_block_traces(gateway_client):
    # docs: get_block_traces_start
    block_traces = await gateway_client.get_block_traces(block_hash="latest")
    # or
    block_traces = await gateway_client.get_block_traces(block_number=0)
    # docs: get_block_traces_end


@pytest.mark.asyncio
async def test_get_state_update(gateway_client):
    # docs: get_state_update_start
    state_update = await gateway_client.get_state_update(block_hash="latest")
    # or
    state_update = await gateway_client.get_state_update(block_number=0)
    # docs: get_state_update_end


@pytest.mark.asyncio
async def test_get_storage_at(gateway_client, map_contract):
    address = map_contract.address
    # docs: get_storage_at_start
    state_update = await gateway_client.get_storage_at(
        contract_address=address,
        key=get_storage_var_address("storage_var name"),
        block_hash="latest",
    )
    # docs: get_storage_at_end


@pytest.mark.asyncio
async def test_get_transaction(gateway_client, declare_transaction_hash):
    transaction_hash = declare_transaction_hash
    # docs: get_get_transaction_start
    transaction = await gateway_client.get_transaction(tx_hash=transaction_hash)
    # docs: get_get_transaction_end
