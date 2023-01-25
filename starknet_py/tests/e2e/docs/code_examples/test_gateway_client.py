# pylint: disable=unused-variable
import pytest
from starkware.starknet.public.abi import (
    get_selector_from_name,
    get_storage_var_address,
)
from starkware.starknet.services.api.contract_class import ContractClass

from starknet_py.net.client_models import Call
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models.transaction import Declare
from starknet_py.net.networks import TESTNET
from starknet_py.tests.e2e.fixtures.misc import read_contract


def test_init():
    # docs-start: init
    gateway_client = GatewayClient(net=TESTNET)
    # or (for custom urls)
    gateway_client = GatewayClient(
        net={"feeder_gateway_url": "some_feeder_url", "gateway_url": "some_gateway_url"}
    )
    # docs-end: init


@pytest.mark.asyncio
async def test_get_block(gateway_client):
    # docs-start: get_block
    block = await gateway_client.get_block(block_hash="latest")
    # or
    block = await gateway_client.get_block(block_number=0)
    # docs-end: get_block


@pytest.mark.asyncio
async def test_get_block_traces(gateway_client):
    # docs-start: get_block_traces
    block_traces = await gateway_client.get_block_traces(block_hash="latest")
    # or
    block_traces = await gateway_client.get_block_traces(block_number=0)
    # docs-end: get_block_traces_end


@pytest.mark.asyncio
async def test_get_state_update(gateway_client):
    # docs-start: get_state_update_start
    state_update = await gateway_client.get_state_update(block_hash="latest")
    # or
    state_update = await gateway_client.get_state_update(block_number=0)
    # docs-end: get_state_update


@pytest.mark.asyncio
async def test_get_storage_at(gateway_client, map_contract):
    address = map_contract.address
    # docs-start: get_storage_at
    state_update = await gateway_client.get_storage_at(
        contract_address=address,
        key=get_storage_var_address("storage_var name"),
        block_hash="latest",
    )
    # docs-end: get_storage_at


@pytest.mark.asyncio
async def test_get_transaction(gateway_client, declare_transaction_hash):
    transaction_hash = declare_transaction_hash
    # docs-start: get_transaction
    transaction = await gateway_client.get_transaction(tx_hash=transaction_hash)
    # docs-end: get_transaction


@pytest.mark.asyncio
async def test_get_transaction_receipt(gateway_client, declare_transaction_hash):
    transaction_hash = declare_transaction_hash
    # docs-start: get_transaction_receipt
    transaction = await gateway_client.get_transaction_receipt(tx_hash=transaction_hash)
    # docs-end: get_transaction_receipt


@pytest.mark.asyncio
async def test_estimate_fee(gateway_account, deploy_account_transaction):
    gateway_client = gateway_account.client
    transaction = deploy_account_transaction
    # docs-start: estimate_fee
    # The transaction can be of type  Invoke | Declare | DeployAccount
    estimated_fee = await gateway_client.estimate_fee(tx=transaction)
    # docs-end: estimate_fee


@pytest.mark.asyncio
async def test_estimate_fee_bulk(gateway_account, deploy_account_transaction):
    gateway_client = gateway_account.client
    transaction1 = deploy_account_transaction
    transaction2 = Declare(
        contract_class=ContractClass.loads(read_contract("map_compiled.json")),
        sender_address=0x1,
        max_fee=0,
        signature=[0x0, 0x0],
        nonce=0,
        version=0,
    )
    # docs-start: estimate_fee_bulk
    # The transactions can be of type  List[Invoke | Declare | DeployAccount]
    list_of_estimated_fees = await gateway_client.estimate_fee_bulk(
        transactions=[transaction1, transaction2]
    )
    # docs-end: estimate_fee_bulk


@pytest.mark.asyncio
async def test_call_contract(gateway_client, contract_address):
    # docs-start: call_contract
    transaction = await gateway_client.call_contract(
        call=Call(
            to_addr=contract_address,
            selector=get_selector_from_name("increase_balance"),
            calldata=[123],
        ),
        block_hash="latest",
    )
    # docs-end: call_contract


@pytest.mark.asyncio
async def test_send_transaction(gateway_client, deploy_account_transaction):
    transaction = deploy_account_transaction
    # docs-start: send_transaction
    sent_transaction_response = await gateway_client.send_transaction(
        transaction=transaction
    )
    # docs-end: send_transaction
