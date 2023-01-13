# pylint: disable=unused-variable, invalid-name
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
    # docs: get_transaction_start
    transaction = await gateway_client.get_transaction(tx_hash=transaction_hash)
    # docs: get_transaction_end


@pytest.mark.asyncio
async def test_get_transaction_receipt(gateway_client, declare_transaction_hash):
    transaction_hash = declare_transaction_hash
    # docs: get_transaction_receipt_start
    transaction = await gateway_client.get_transaction_receipt(tx_hash=transaction_hash)
    # docs: get_transaction_receipt_end


@pytest.mark.asyncio
async def test_estimate_fee(gateway_account, deploy_account_transaction):
    gateway_client = gateway_account.client
    transaction = deploy_account_transaction
    # docs: estimate_fee_start
    # The transaction can be of type  Invoke | Declare | DeployAccount
    estimated_fee = await gateway_client.estimate_fee(tx=transaction)
    # docs: estimate_fee_end


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
    # docs: estimate_fee_bulk_start
    # The transactions can be of type  List[Invoke | Declare | DeployAccount]
    list_of_estimated_fees = await gateway_client.estimate_fee_bulk(
        transactions=[transaction1, transaction2]
    )
    # docs: estimate_fee_bulk_end


@pytest.mark.asyncio
async def test_call_contract(gateway_client, contract_address):
    # docs: call_contract_start
    transaction = await gateway_client.call_contract(
        call=Call(
            to_addr=contract_address,
            selector=get_selector_from_name("increase_balance"),
            calldata=[123],
        ),
        block_hash="latest",
    )
    # docs: call_contract_end


@pytest.mark.asyncio
async def test_send_transaction(gateway_client, deploy_account_transaction):
    transaction = deploy_account_transaction
    # docs: send_transaction_start
    sent_transaction_response = await gateway_client.send_transaction(transaction=transaction)
    # docs: send_transaction_end
