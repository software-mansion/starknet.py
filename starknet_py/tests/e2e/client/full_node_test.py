import pytest
from starkware.starknet.services.api.gateway.transaction import DECLARE_SENDER_ADDRESS

from starknet_py.net.client_errors import ClientError
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
    tx = await rpc_client.get_transaction_by_block_id(block_number=1, index=0)

    assert tx == DeployTransaction(
        hash=deploy_transaction_hash,
        contract_address=contract_address,
        constructor_calldata=[],
        max_fee=0,
        signature=[],
        class_hash=class_hash,
    )


@pytest.mark.asyncio
async def test_node_get_declare_transaction_by_block_number_and_index(
    declare_transaction_hash, rpc_client, class_hash
):
    tx = await rpc_client.get_transaction_by_block_id(block_number=3, index=0)

    assert tx == DeclareTransaction(
        class_hash=class_hash,
        sender_address=DECLARE_SENDER_ADDRESS,
        hash=declare_transaction_hash,
        signature=[],
        max_fee=0,
    )


@pytest.mark.asyncio
async def test_get_class_at(rpc_client, contract_address):
    declared_contract = await rpc_client.get_class_at(
        contract_address=contract_address, block_hash="latest"
    )

    assert declared_contract.program != {}
    assert declared_contract.entry_points_by_type is not None


@pytest.mark.asyncio
async def test_get_class_at_throws_on_wrong_address(rpc_client):
    with pytest.raises(ClientError) as err:
        await rpc_client.get_class_at(contract_address=0, block_hash="latest")

    assert "Client failed with code 20: Contract not found" == str(err.value)


@pytest.mark.asyncio
async def test_block_transaction_count(rpc_client):
    latest_block = (await rpc_client.get_block("latest")).block_number

    for block_number in range(1, latest_block):
        transaction_count = await rpc_client.get_block_transaction_count(
            block_number=block_number
        )

        assert transaction_count == 1


@pytest.mark.asyncio
async def test_method_raises_on_both_block_hash_and_number(rpc_client):
    with pytest.raises(ValueError) as err:
        await rpc_client.get_block(block_number=0, block_hash="0x0")

    assert "Block_hash and block_number parameters are mutually exclusive." == str(
        err.value
    )
