import pytest

from starknet_py.net.client_models import TransactionType
from starknet_py.net.base_client import BlockHashIdentifier, BlockNumberIdentifier
from starknet_py.tests.e2e.utils import DevnetClientFactory


@pytest.mark.asyncio
async def test_node_get_transaction_block_hash_identifier(
    devnet_address, block_hash, deploy_transaction_hash, contract_address
):
    client = await DevnetClientFactory(devnet_address).make_rpc_client()
    identifier: BlockHashIdentifier = {"block_hash": int(block_hash, 16), "index": 0}

    tx = await client.get_transaction(tx_identifier=identifier)

    assert tx.hash == deploy_transaction_hash
    assert tx.contract_address == contract_address
    assert tx.calldata == []
    assert tx.entry_point_selector == 0
    assert tx.transaction_type == TransactionType.DEPLOY
    assert tx.version == 0
    assert tx.max_fee == 0


@pytest.mark.asyncio
async def test_node_get_transaction_block_number_identifier(
    devnet_address, deploy_transaction_hash, contract_address
):
    client = await DevnetClientFactory(devnet_address).make_rpc_client()
    identifier: BlockNumberIdentifier = {"block_number": 0, "index": 0}

    tx = await client.get_transaction(tx_identifier=identifier)

    assert tx.hash == deploy_transaction_hash
    assert tx.contract_address == contract_address
    assert tx.calldata == []
    assert tx.entry_point_selector == 0
    assert tx.transaction_type == TransactionType.DEPLOY
    assert tx.version == 0
    assert tx.max_fee == 0
