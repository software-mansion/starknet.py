# pylint: disable=unused-variable
import pytest
from starkware.starknet.public.abi import (
    get_selector_from_name,
    get_storage_var_address,
)

from starknet_py.net.client_models import Call
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.networks import TESTNET


def test_init():
    # docs-start: init
    full_node_client = FullNodeClient(node_url="https://your.node.url", net=TESTNET)
    # docs-end: init


@pytest.mark.asyncio
async def test_get_block(full_node_client):
    # docs-start: get_block
    block = await full_node_client.get_block(block_number="latest")
    block = await full_node_client.get_block(block_number=0)
    # or
    block = await full_node_client.get_block(block_hash="0x0")
    # docs-end: get_block


@pytest.mark.asyncio
async def test_get_state_update(full_node_client):
    # docs-start: get_state_update
    state_update = await full_node_client.get_state_update(block_number="latest")
    state_update = await full_node_client.get_state_update(block_number=0)
    # or
    state_update = await full_node_client.get_state_update(block_hash="0x0")
    # docs-end: get_state_update


@pytest.mark.asyncio
async def test_get_storage_at(full_node_client, map_contract):
    address = map_contract.address
    # docs-start: get_storage_at
    storage_value = await full_node_client.get_storage_at(
        contract_address=address,
        key=get_storage_var_address("storage_var name"),
        block_number="latest",
    )
    # docs-end: get_storage_at


@pytest.mark.asyncio
async def test_get_transaction(full_node_client, declare_transaction_hash):
    # docs-start: get_transaction
    transaction_hash = 0x1 or 1 or "0x1"
    # docs-end: get_transaction
    transaction_hash = declare_transaction_hash
    # docs-start: get_transaction
    transaction = await full_node_client.get_transaction(tx_hash=transaction_hash)
    # docs-end: get_transaction


@pytest.mark.asyncio
async def test_get_transaction_receipt(full_node_client, declare_transaction_hash):
    transaction_hash = declare_transaction_hash
    # docs-start: get_transaction_receipt
    transaction_receipt = await full_node_client.get_transaction_receipt(
        tx_hash=transaction_hash
    )
    # docs-end: get_transaction_receipt


@pytest.mark.asyncio
async def test_estimate_fee(full_node_account, deploy_account_transaction):
    full_node_client = full_node_account.client
    transaction = deploy_account_transaction
    # docs-start: estimate_fee
    estimated_fee = await full_node_client.estimate_fee(tx=transaction)
    # docs-end: estimate_fee


@pytest.mark.asyncio
async def test_call_contract(full_node_client, contract_address):
    # docs-start: call_contract
    response = await full_node_client.call_contract(
        call=Call(
            to_addr=contract_address,
            selector=get_selector_from_name("increase_balance"),
            calldata=[123],
        ),
        block_number="latest",
    )
    # docs-end: call_contract


@pytest.mark.asyncio
async def test_get_class_hash_at(full_node_client, contract_address):
    # docs-start: get_class_hash_at
    address = 0x1 or 1 or "0x1"
    # docs-end: get_class_hash_at
    address = contract_address
    # docs-start: get_class_hash_at
    class_hash = await full_node_client.get_class_hash_at(
        contract_address=address, block_number="latest"
    )
    # docs-end: get_class_hash_at


@pytest.mark.asyncio
async def test_get_class_by_hash(full_node_client, class_hash):
    # docs-start: get_class_by_hash
    hash_ = 0x1 or 1 or "0x1"
    # docs-end: get_class_by_hash
    hash_ = class_hash
    # docs-start: get_class_by_hash
    contract_class = await full_node_client.get_class_by_hash(class_hash=hash_)
    # docs-end: get_class_by_hash


@pytest.mark.asyncio
async def test_get_transaction_by_block_id(full_node_client):
    # docs-start: get_transaction_by_block_id
    transaction = await full_node_client.get_transaction_by_block_id(
        index=0, block_number="latest"
    )
    # docs-end: get_transaction_by_block_id


@pytest.mark.asyncio
async def test_get_block_transaction_count(full_node_client):
    # docs-start: get_block_transaction_count
    num_of_transactions = await full_node_client.get_block_transaction_count(
        block_number="latest"
    )
    # docs-end: get_block_transaction_count


@pytest.mark.asyncio
async def test_get_class_at(full_node_client, contract_address):
    # docs-start: get_class_at
    address = 0x1 or 1 or "0x1"
    # docs-end: get_class_at
    address = contract_address
    # docs-start: get_class_at
    contract_class = await full_node_client.get_class_at(
        contract_address=address, block_number="latest"
    )
    # docs-end: get_class_at


@pytest.mark.asyncio
async def test_get_contract_nonce(full_node_client, contract_address):
    # docs-start: get_contract_nonce
    address = 0x1 or 1 or "0x1"
    # docs-end: get_contract_nonce
    address = contract_address
    # docs-start: get_contract_nonce
    nonce = await full_node_client.get_contract_nonce(
        contract_address=address, block_number="latest"
    )
    # docs-end: get_contract_nonce
