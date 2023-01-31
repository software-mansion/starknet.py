# pylint: disable=unused-variable
import pytest
from starkware.starknet.public.abi import (
    get_selector_from_name,
    get_storage_var_address,
)

from starknet_py.net.client_models import Call
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.networks import TESTNET
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


def test_init():
    # docs-start: init
    gateway_client = GatewayClient(net=TESTNET)
    # or when using custom urls
    gateway_client = GatewayClient(
        net={
            "feeder_gateway_url": "https://alpha4.starknet.io/feeder_gateway",
            "gateway_url": "https://alpha4.starknet.io/gateway",
        }
    )
    # docs-end: init


@pytest.mark.asyncio
async def test_get_block(gateway_client):
    # docs-start: get_block
    block = await gateway_client.get_block(block_number="latest")
    block = await gateway_client.get_block(block_number=0)
    # or
    block = await gateway_client.get_block(block_hash="0x0")
    # docs-end: get_block


@pytest.mark.asyncio
async def test_get_block_traces(gateway_client):
    # docs-start: get_block_traces
    block_traces = await gateway_client.get_block_traces(block_number="latest")
    block_traces = await gateway_client.get_block_traces(block_number=0)
    # or
    block_traces = await gateway_client.get_block_traces(block_hash="0x0")
    # docs-end: get_block_traces


@pytest.mark.asyncio
async def test_get_state_update(gateway_client):
    # docs-start: get_state_update
    state_update = await gateway_client.get_state_update(block_number="latest")
    state_update = await gateway_client.get_state_update(block_number=0)
    # or
    state_update = await gateway_client.get_state_update(block_hash="0x0")
    # docs-end: get_state_update


@pytest.mark.asyncio
async def test_get_storage_at(gateway_client, map_contract):
    address = map_contract.address
    # docs-start: get_storage_at
    storage_value = await gateway_client.get_storage_at(
        contract_address=address,
        key=get_storage_var_address("name_of_storage_var"),
        block_number="latest",
    )
    # docs-end: get_storage_at


@pytest.mark.asyncio
async def test_get_transaction(gateway_client, declare_transaction_hash):
    # docs-start: get_transaction
    transaction_hash = 0x1 or 1 or "0x1"
    # docs-end: get_transaction
    transaction_hash = declare_transaction_hash
    # docs-start: get_transaction
    transaction = await gateway_client.get_transaction(tx_hash=transaction_hash)
    # docs-end: get_transaction


@pytest.mark.asyncio
async def test_get_transaction_receipt(gateway_client, declare_transaction_hash):
    transaction_hash = declare_transaction_hash
    # docs-start: get_transaction_receipt
    transaction_receipt = await gateway_client.get_transaction_receipt(
        tx_hash=transaction_hash
    )
    # docs-end: get_transaction_receipt


@pytest.mark.asyncio
async def test_estimate_fee(gateway_account, deploy_account_transaction):
    gateway_client = gateway_account.client
    transaction = deploy_account_transaction
    # docs-start: estimate_fee
    estimated_fee = await gateway_client.estimate_fee(tx=transaction)
    # docs-end: estimate_fee


@pytest.mark.asyncio
async def test_estimate_fee_bulk(
    gateway_account, deploy_account_transaction, map_compiled_contract
):
    gateway_client = gateway_account.client
    transaction1 = deploy_account_transaction
    transaction2 = await gateway_account.sign_declare_transaction(
        compiled_contract=map_compiled_contract, max_fee=MAX_FEE
    )
    # docs-start: estimate_fee_bulk
    list_of_estimated_fees = await gateway_client.estimate_fee_bulk(
        transactions=[transaction1, transaction2]
    )
    # docs-end: estimate_fee_bulk


@pytest.mark.asyncio
async def test_call_contract(gateway_client, contract_address):
    # docs-start: call_contract
    response = await gateway_client.call_contract(
        call=Call(
            to_addr=contract_address,
            selector=get_selector_from_name("increase_balance"),
            calldata=[123],
        ),
        block_number="latest",
    )
    # docs-end: call_contract


@pytest.mark.asyncio
async def test_get_class_hash_at(gateway_client, contract_address):
    # docs-start: get_class_hash_at
    address = 0x1 or 1 or "0x1"
    # docs-end: get_class_hash_at
    address = contract_address
    # docs-start: get_class_hash_at
    class_hash = await gateway_client.get_class_hash_at(
        contract_address=address, block_number="latest"
    )
    # docs-end: get_class_hash_at


@pytest.mark.asyncio
async def test_get_class_by_hash(gateway_client, class_hash):
    # docs-start: get_class_by_hash
    hash_ = 0x1 or 1 or "0x1"
    # docs-end: get_class_by_hash
    hash_ = class_hash
    # docs-start: get_class_by_hash
    contract_class = await gateway_client.get_class_by_hash(class_hash=hash_)
    # docs-end: get_class_by_hash


@pytest.mark.asyncio
async def test_get_transaction_status(gateway_client, invoke_transaction_hash):
    # docs-start: get_transaction_status
    transaction_hash = 0x1 or 1 or "0x1"
    # docs-end: get_transaction_status
    transaction_hash = invoke_transaction_hash
    # docs-start: get_transaction_status
    status_response = await gateway_client.get_transaction_status(
        tx_hash=transaction_hash
    )
    # docs-end: get_transaction_status


@pytest.mark.asyncio
async def test_get_code(gateway_client, contract_address):
    # docs-start: get_code
    address = 0x1 or 1 or "0x1"
    # docs-end: get_code
    address = contract_address
    # docs-start: get_code
    code = await gateway_client.get_code(
        contract_address=address, block_number="latest"
    )
    # docs-end: get_code


@pytest.mark.asyncio
async def test_get_contract_nonce(gateway_client, contract_address):
    # docs-start: get_contract_nonce
    address = 0x1 or 1 or "0x1"
    # docs-end: get_contract_nonce
    address = contract_address
    # docs-start: get_contract_nonce
    nonce = await gateway_client.get_contract_nonce(
        contract_address=address, block_number="latest"
    )
    # docs-end: get_contract_nonce
