import pytest
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.gateway.transaction import DECLARE_SENDER_ADDRESS

from starknet_py.net.client_models import (
    DeclareTransaction,
    DeployTransaction,
    InvokeFunction,
)


@pytest.mark.asyncio
async def test_node_get_transaction_by_block_hash_and_index(
    block_with_deploy_hash, deploy_transaction_hash, contract_address, rpc_client
):
    tx = await rpc_client.get_transaction_by_block_hash(
        block_hash=block_with_deploy_hash, index=0
    )

    assert tx == DeployTransaction(
        hash=deploy_transaction_hash,
        contract_address=contract_address,
        constructor_calldata=[],
        max_fee=0,
        signature=[],
        # class_hash=class_hash,
    )


@pytest.mark.asyncio
async def test_node_get_deploy_transaction_by_block_number_and_index(
    deploy_transaction_hash, contract_address, rpc_client
):
    tx = await rpc_client.get_transaction_by_block_number(block_number=0, index=0)

    assert tx == DeployTransaction(
        hash=deploy_transaction_hash,
        contract_address=contract_address,
        constructor_calldata=[],
        max_fee=0,
        signature=[],
        # class_hash=class_hash,
    )


@pytest.mark.asyncio
async def test_get_block_throws_on_no_block_hash_and_no_number(rpc_client):
    with pytest.raises(ValueError) as exinfo:
        await rpc_client.get_block()

    assert "Either block_hash or block_number is required" in str(exinfo.value)


@pytest.mark.asyncio
async def test_call_contract_raises_on_no_block_hash(clients, contract_address):
    _, client = clients
    invoke_function = InvokeFunction(
        contract_address=contract_address,
        entry_point_selector=get_selector_from_name("get_balance"),
        calldata=[],
        max_fee=0,
        version=0,
        signature=[0x0, 0x0],
    )

    with pytest.raises(ValueError) as exinfo:
        await client.call_contract(invoke_tx=invoke_function)

    assert "block_hash is required" in str(exinfo.value)


# This test will fail as in RPC 0.15.0 specification DECLARE_TXN has contract_class as a key
# In RPC 0.20.0 the field changed to class_hash and the change is yet to be implemented in devnet
@pytest.mark.xfail
@pytest.mark.asyncio
async def test_node_get_declare_transaction_by_block_number_and_index(
    declare_transaction_hash, rpc_client, class_hash
):
    tx = await rpc_client.get_transaction_by_block_number(block_number=0, index=0)

    assert tx == DeclareTransaction(
        class_hash=class_hash,
        sender_address=DECLARE_SENDER_ADDRESS,
        hash=declare_transaction_hash,
        signature=[],
        max_fee=0,
    )
