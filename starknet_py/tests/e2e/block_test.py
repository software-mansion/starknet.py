import pytest

from starknet_py.net.client_models import (
    BlockStatus,
    L1DAMode,
    PendingStarknetBlock,
    PendingStarknetBlockWithTxHashes,
    StarknetBlock,
    StarknetBlockWithReceipts,
    StarknetBlockWithTxHashes,
)


@pytest.mark.asyncio
async def test_pending_block(account):
    blk = await account.client.get_block(block_number="pending")
    assert blk.transactions is not None
    assert isinstance(blk, PendingStarknetBlock)


@pytest.mark.asyncio
async def test_latest_block(account):
    blk = await account.client.get_block(block_number="latest")
    assert blk.block_hash
    assert blk.transactions is not None
    assert isinstance(blk, StarknetBlock)


@pytest.mark.asyncio
async def test_block_with_tx_hashes_pending(account):
    blk = await account.client.get_block_with_tx_hashes(block_number="pending")

    assert isinstance(blk, PendingStarknetBlockWithTxHashes)
    assert isinstance(blk.transactions, list)


# TODO (#1419): Fix contract redeclaration
@pytest.mark.skip(reason="Redeclaration occurred")
@pytest.mark.asyncio
async def test_block_with_tx_hashes_latest(
    account,
    map_contract_declare_hash,
):
    blk = await account.client.get_block_with_tx_hashes(block_number="latest")

    assert isinstance(blk, StarknetBlockWithTxHashes)
    assert isinstance(blk.transactions, list)
    assert map_contract_declare_hash in blk.transactions
    assert blk.block_hash is not None
    assert blk.parent_hash is not None
    assert blk.block_number is not None
    assert blk.new_root is not None
    assert blk.timestamp is not None
    assert blk.sequencer_address is not None
    assert blk.l1_gas_price.price_in_wei > 0
    assert blk.l1_gas_price.price_in_fri > 0
    assert blk.l1_data_gas_price.price_in_wei >= 0
    assert blk.l1_data_gas_price.price_in_fri >= 0
    assert blk.l1_da_mode in L1DAMode


@pytest.mark.asyncio
async def test_get_block_with_txs_pending(account):
    blk = await account.client.get_block_with_txs(block_number="pending")

    assert isinstance(blk, PendingStarknetBlock)
    assert isinstance(blk.transactions, list)


# TODO (#1419): Fix contract redeclaration
@pytest.mark.skip(reason="Redeclaration occurred")
@pytest.mark.asyncio
async def test_get_block_with_txs_latest(
    account,
    map_contract_declare_hash,
):
    blk = await account.client.get_block_with_txs(block_number="latest")

    assert isinstance(blk, StarknetBlock)
    assert isinstance(blk.transactions, list)
    assert blk.transactions[0].hash == map_contract_declare_hash
    assert blk.block_hash is not None
    assert blk.parent_hash is not None
    assert blk.block_number is not None
    assert blk.new_root is not None
    assert blk.timestamp is not None
    assert blk.sequencer_address is not None
    assert blk.l1_gas_price.price_in_wei > 0
    assert blk.l1_gas_price.price_in_fri > 0
    assert blk.l1_data_gas_price.price_in_wei >= 0
    assert blk.l1_data_gas_price.price_in_fri >= 0
    assert blk.l1_da_mode in L1DAMode


@pytest.mark.asyncio
async def test_block_with_receipts_latest(account):
    blk = await account.client.get_block_with_receipts(block_number="latest")

    assert isinstance(blk, StarknetBlockWithReceipts)
    assert isinstance(blk.transactions, list)
    assert blk.status == BlockStatus.ACCEPTED_ON_L2
    assert blk.block_hash is not None
    assert blk.parent_hash is not None
    assert blk.block_number is not None
    assert blk.new_root is not None
    assert blk.timestamp is not None
    assert blk.sequencer_address is not None
    assert blk.l1_gas_price.price_in_wei > 0
    assert blk.l1_gas_price.price_in_fri > 0
    assert blk.l1_data_gas_price.price_in_wei >= 0
    assert blk.l1_data_gas_price.price_in_fri >= 0
    assert blk.l1_da_mode in L1DAMode
