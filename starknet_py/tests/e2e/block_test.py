import sys

import pytest

from starknet_py.contract import Contract
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client_models import (
    GatewayBlock,
    PendingStarknetBlock,
    PendingStarknetBlockWithTxHashes,
    StarknetBlock,
    StarknetBlockWithTxHashes,
)
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


async def declare_contract(account: BaseAccount, compiled_contract: str):
    declare_result = await Contract.declare(
        account=account,
        compiled_contract=compiled_contract,
        max_fee=MAX_FEE,
    )
    await declare_result.wait_for_acceptance()


# TODO (#1154): remove line below
@pytest.mark.xfail(
    "--client=gateway" in sys.argv,
    reason="0.12.2 returns Felts in state_root, devnet returns NonPrefixedHex",
)
@pytest.mark.asyncio
async def test_pending_block(account, map_compiled_contract):
    await declare_contract(account, map_compiled_contract)

    blk = await account.client.get_block(block_number="pending")
    assert blk.transactions is not None
    if isinstance(account.client, GatewayClient):
        assert blk.block_hash
        assert isinstance(blk, GatewayBlock)
    else:
        assert isinstance(blk, PendingStarknetBlock)


# TODO (#1154): remove line below
@pytest.mark.xfail(
    "--client=gateway" in sys.argv,
    reason="0.12.2 returns Felts in state_root, devnet returns NonPrefixedHex",
)
@pytest.mark.asyncio
async def test_latest_block(account, map_compiled_contract):
    await declare_contract(account, map_compiled_contract)

    blk = await account.client.get_block(block_number="latest")
    assert blk.block_hash
    assert blk.transactions is not None
    if isinstance(account.client, GatewayClient):
        assert isinstance(blk, GatewayBlock)
    else:
        assert isinstance(blk, StarknetBlock)


@pytest.mark.asyncio
async def test_block_with_tx_hashes_pending(
    full_node_account,
):
    blk = await full_node_account.client.get_block_with_tx_hashes(
        block_number="pending"
    )

    assert isinstance(blk, PendingStarknetBlockWithTxHashes)
    assert isinstance(blk.transactions, list)


@pytest.mark.asyncio
async def test_block_with_tx_hashes_latest(
    full_node_account,
    map_contract_declare_hash,
):
    blk = await full_node_account.client.get_block_with_tx_hashes(block_number="latest")

    assert isinstance(blk, StarknetBlockWithTxHashes)
    assert isinstance(blk.transactions, list)
    assert map_contract_declare_hash in blk.transactions
    assert blk.block_hash is not None
    assert blk.parent_block_hash is not None
    assert blk.block_number is not None
    assert blk.root is not None
    assert blk.timestamp is not None
    assert blk.sequencer_address is not None


@pytest.mark.asyncio
async def test_get_block_with_txs_pending(
    full_node_account,
):
    blk = await full_node_account.client.get_block_with_txs(block_number="pending")

    assert isinstance(blk, PendingStarknetBlock)
    assert isinstance(blk.transactions, list)


@pytest.mark.asyncio
async def test_get_block_with_txs_latest(
    full_node_account,
    map_contract_declare_hash,
):
    blk = await full_node_account.client.get_block_with_txs(block_number="latest")

    assert isinstance(blk, StarknetBlock)
    assert isinstance(blk.transactions, list)
    assert blk.transactions[0].hash == map_contract_declare_hash
    assert blk.block_hash is not None
    assert blk.parent_block_hash is not None
    assert blk.block_number is not None
    assert blk.root is not None
    assert blk.timestamp is not None
    assert blk.sequencer_address is not None
