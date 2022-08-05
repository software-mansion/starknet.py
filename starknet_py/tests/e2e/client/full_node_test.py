import pytest
from starkware.starknet.services.api.gateway.transaction import DECLARE_SENDER_ADDRESS

from starknet_py.net.client_models import (
    DeclareTransaction,
    DeployTransaction,
)


@pytest.mark.asyncio
async def test_node_get_transaction_by_block_id_and_index(
    block_with_deploy_hash,
    deploy_transaction_hash,
    contract_address,
    rpc_client,
    class_hash,
):
    tx = await rpc_client.get_transaction_by_block_id(
        block_hash=block_with_deploy_hash, index=0
    )

    assert tx == DeployTransaction(
        hash=deploy_transaction_hash,
        contract_address=contract_address,
        constructor_calldata=[],
        max_fee=0,
        signature=[],
        class_hash=class_hash,
    )


@pytest.mark.asyncio
async def test_node_get_deploy_transaction_by_block_id_and_index(
    deploy_transaction_hash, contract_address, rpc_client, class_hash
):
    tx = await rpc_client.get_transaction_by_block_number(block_number=1, index=0)

    assert tx == DeployTransaction(
        hash=deploy_transaction_hash,
        contract_address=contract_address,
        constructor_calldata=[],
        max_fee=0,
        signature=[],
        class_hash=class_hash,
    )


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
