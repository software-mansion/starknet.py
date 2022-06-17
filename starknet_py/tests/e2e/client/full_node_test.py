import pytest

from starknet_py.net.client_models import TransactionType
from starknet_py.net.client_models import InvokeFunction
from starknet_py.tests.e2e.utils import DevnetClientFactory


@pytest.mark.asyncio
async def test_node_get_transaction_by_block_hash_and_index(
    devnet_address, block_hash, deploy_transaction_hash, contract_address
):
    client = await DevnetClientFactory(devnet_address).make_rpc_client()

    tx = await client.get_transaciton_by_block_hash_and_index(
        block_hash=int(block_hash, 16), index=0
    )

    assert tx.hash == deploy_transaction_hash
    assert tx.contract_address == contract_address
    assert tx.calldata == []
    assert tx.entry_point_selector == 0
    assert tx.transaction_type == TransactionType.DEPLOY
    assert tx.version == 0
    assert tx.max_fee == 0


@pytest.mark.asyncio
async def test_node_get_transaction_by_block_number_and_index(
    devnet_address, deploy_transaction_hash, contract_address
):
    client = await DevnetClientFactory(devnet_address).make_rpc_client()

    tx = await client.get_transaciton_by_block_number_and_index(block_number=0, index=0)

    assert tx.hash == deploy_transaction_hash
    assert tx.contract_address == contract_address
    assert tx.calldata == []
    assert tx.entry_point_selector == 0
    assert tx.transaction_type == TransactionType.DEPLOY
    assert tx.version == 0
    assert tx.max_fee == 0


@pytest.mark.asyncio
async def test_get_block_throws_on_no_block_hash_and_no_number(
    devnet_address, block_hash
):
    client = await DevnetClientFactory(devnet_address).make_rpc_client()

    with pytest.raises(ValueError) as exinfo:
        await client.get_block()

    assert "Block_hash or block_number must be provided" in str(exinfo.value)


@pytest.mark.asyncio
async def test_get_storage_at_throws_on_no_block_hash(devnet_address):
    client = await DevnetClientFactory(devnet_address).make_rpc_client()

    with pytest.raises(ValueError) as exinfo:
        await client.get_storage_at(contract_address=0x0, key=0x0)

    assert "Block_hash must be provided when using FullNodeClient" in str(exinfo.value)


@pytest.mark.asyncio
async def test_call_contract_throws_at_no_block_hash(devnet_address, contract_address):
    client = await DevnetClientFactory(devnet_address).make_rpc_client()

    with pytest.raises(ValueError) as exinfo:
        await client.call_contract(
            invoke_tx=InvokeFunction(
                contract_address=contract_address,
                entry_point_selector=0x1,
                calldata=[],
                max_fee=0,
                version=0,
                signature=[],
            )
        )

    assert "Block_hash must be provided when using FullNodeClient" in str(exinfo.value)
