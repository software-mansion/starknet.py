import pytest

from starknet_py.net.client_models import (
    BlockTransactionTracesWithInitialReads,
    InvokeTransactionV3,
    StorageResponseFlag,
    StorageResult,
    TraceFlag,
    TransactionResponseFlag,
)
from starknet_py.net.full_node_client import FullNodeClient

# Transaction with proof and proof_facts on the integration network
INVOKE_WITH_PROOF_TX_HASH = (
    0x25A063A20442720ABBA3E44F6015204E5422F3661198A2D4545F90E463C1FC6
)


@pytest.mark.asyncio
async def test_get_transaction_with_proof_facts(client_integration: FullNodeClient):
    transaction = await client_integration.get_transaction(
        tx_hash=INVOKE_WITH_PROOF_TX_HASH,
        response_flags=[TransactionResponseFlag.INCLUDE_PROOF_FACTS],
    )

    assert isinstance(transaction, InvokeTransactionV3)
    assert transaction.hash == INVOKE_WITH_PROOF_TX_HASH
    assert transaction.proof_facts is not None
    assert len(transaction.proof_facts) > 0


@pytest.mark.asyncio
async def test_get_block_with_txs_response_flags(client_integration: FullNodeClient):
    tx = await client_integration.get_transaction(tx_hash=INVOKE_WITH_PROOF_TX_HASH)
    receipt = await client_integration.get_transaction_receipt(
        tx_hash=INVOKE_WITH_PROOF_TX_HASH
    )

    block = await client_integration.get_block_with_txs(
        block_number=receipt.block_number,
        response_flags=[TransactionResponseFlag.INCLUDE_PROOF_FACTS],
    )

    assert block.block_number == receipt.block_number
    matching = [t for t in block.transactions if t.hash == tx.hash]
    assert len(matching) == 1
    assert isinstance(matching[0], InvokeTransactionV3)
    assert matching[0].proof_facts is not None
    assert len(matching[0].proof_facts) > 0


@pytest.mark.asyncio
async def test_get_block_with_tx_hashes_response_flags(
    client_integration: FullNodeClient,
):
    receipt = await client_integration.get_transaction_receipt(
        tx_hash=INVOKE_WITH_PROOF_TX_HASH
    )

    block = await client_integration.get_block_with_tx_hashes(
        block_number=receipt.block_number,
        response_flags=[TransactionResponseFlag.INCLUDE_PROOF_FACTS],
    )

    assert block.block_number == receipt.block_number
    assert INVOKE_WITH_PROOF_TX_HASH in block.transactions


@pytest.mark.asyncio
async def test_get_block_with_receipts_response_flags(
    client_integration: FullNodeClient,
):
    receipt = await client_integration.get_transaction_receipt(
        tx_hash=INVOKE_WITH_PROOF_TX_HASH
    )

    block = await client_integration.get_block_with_receipts(
        block_number=receipt.block_number,
        response_flags=[TransactionResponseFlag.INCLUDE_PROOF_FACTS],
    )

    assert block.block_number == receipt.block_number
    assert len(block.transactions) > 0


@pytest.mark.asyncio
async def test_get_storage_at_with_include_last_update_block(
    client_integration: FullNodeClient,
):
    from starknet_py.hash.storage import get_storage_var_address

    # Use TestToken fee contract as a known deployed contract
    test_token_address = (
        0x7B19E89252B1EE5D7FF07A0E0E278B16B058F322053F799469B969E31B82969
    )
    storage = await client_integration.get_storage_at(
        contract_address=test_token_address,
        key=get_storage_var_address("ERC20_total_supply"),
        block_hash="latest",
        response_flags=[StorageResponseFlag.INCLUDE_LAST_UPDATE_BLOCK],
    )

    assert isinstance(storage, StorageResult)
    assert storage.last_update_block is not None


@pytest.mark.asyncio
async def test_trace_block_transactions_return_initial_reads(
    client_integration: FullNodeClient,
):
    receipt = await client_integration.get_transaction_receipt(
        tx_hash=INVOKE_WITH_PROOF_TX_HASH
    )

    result = await client_integration.trace_block_transactions(
        block_number=receipt.block_number,
        trace_flags=[TraceFlag.RETURN_INITIAL_READS],
    )

    assert isinstance(result, BlockTransactionTracesWithInitialReads)
    assert len(result.transaction_traces) > 0
    assert result.initial_reads is not None
