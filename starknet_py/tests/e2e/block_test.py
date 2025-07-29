import pytest

from starknet_py.net.client_models import (
    BlockStatus,
    L1DAMode,
    PreConfirmedStarknetBlock,
    PreConfirmedStarknetBlockWithTxHashes,
    StarknetBlock,
    StarknetBlockWithReceipts,
    StarknetBlockWithTxHashes,
)


@pytest.mark.asyncio
async def test_pre_confirmed_block(account):
    blk = await account.client.get_block(block_number="pre_confirmed")
    assert blk.transactions is not None
    assert isinstance(blk, PreConfirmedStarknetBlock)


@pytest.mark.asyncio
async def test_latest_block(account):
    blk = await account.client.get_block(block_number="latest")
    assert blk.block_hash
    assert blk.transactions is not None
    assert isinstance(blk, StarknetBlock)


@pytest.mark.asyncio
async def test_block_with_tx_hashes_pre_confirmed(account):
    blk = await account.client.get_block_with_tx_hashes(block_number="pre_confirmed")

    assert isinstance(blk, PreConfirmedStarknetBlockWithTxHashes)
    assert isinstance(blk.transactions, list)


@pytest.mark.asyncio
async def test_block_with_tx_hashes_latest(account):
    blk = await account.client.get_block_with_tx_hashes(block_number="latest")

    assert isinstance(blk, StarknetBlockWithTxHashes)
    assert isinstance(blk.transactions, list)
    assert blk.transactions is not None
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
async def test_get_block_with_txs_pre_confirmed(account):
    blk = await account.client.get_block_with_txs(block_number="pre_confirmed")

    assert isinstance(blk, PreConfirmedStarknetBlock)
    assert isinstance(blk.transactions, list)


@pytest.mark.asyncio
async def test_get_block_with_txs_latest(account, map_class_hash):
    # pylint: disable=unused-argument

    blk = await account.client.get_block_with_txs(block_number="latest")

    assert isinstance(blk, StarknetBlock)
    assert isinstance(blk.transactions, list)
    assert blk.transactions[0].hash is not None
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
    assert blk.l2_gas_price.price_in_wei > 0
    assert blk.l2_gas_price.price_in_fri > 0
    assert blk.l1_da_mode in L1DAMode
