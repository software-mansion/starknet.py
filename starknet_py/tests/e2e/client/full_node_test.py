import pytest

from starknet_py.net.client_models import TransactionType, Transaction
from starknet_py.tests.e2e.utils import DevnetClientFactory


@pytest.mark.asyncio
async def test_node_get_transaction_by_block_hash_and_index(
    devnet_address, block_with_deploy_hash, deploy_transaction_hash, contract_address
):
    client = await DevnetClientFactory(devnet_address).make_rpc_client()

    tx = await client.get_transaction_by_block_hash(
        block_hash=block_with_deploy_hash, index=0
    )

    assert tx == Transaction(
        hash=deploy_transaction_hash,
        contract_address=contract_address,
        calldata=[],
        entry_point_selector=0x0,
        transaction_type=TransactionType.DEPLOY,
        version=0,
        max_fee=0,
        signature=[],
    )


@pytest.mark.asyncio
async def test_node_get_transaction_by_block_number_and_index(
    devnet_address, deploy_transaction_hash, contract_address
):
    client = await DevnetClientFactory(devnet_address).make_rpc_client()

    tx = await client.get_transaction_by_block_number(block_number=0, index=0)

    assert tx == Transaction(
        hash=deploy_transaction_hash,
        contract_address=contract_address,
        calldata=[],
        entry_point_selector=0x0,
        transaction_type=TransactionType.DEPLOY,
        version=0,
        max_fee=0,
        signature=[],
    )


@pytest.mark.asyncio
async def test_get_block_throws_on_no_block_hash_and_no_number(devnet_address):
    client = await DevnetClientFactory(devnet_address).make_rpc_client()

    with pytest.raises(ValueError) as exinfo:
        await client.get_block()

    assert "Block_hash or block_number must be provided" in str(exinfo.value)
