import pytest

from starknet_py.net.client_models import InvokeTransactionV3, TransactionResponseFlag
from starknet_py.net.full_node_client import FullNodeClient

# Transaction with proof and proof_facts on the integration network
INVOKE_WITH_PROOF_TX_HASH = (
    0x25A063A20442720ABBA3E44F6015204E5422F3661198A2D4545F90E463C1FC6
)

EXPECTED_PROOF_FACTS = [
    0x50524F4F4630,
    0x5649525455414C5F534E4F53,
    0x3E98C2D7703B03A7EDB73ED7F075F97F1DCBAA8F717CDF6E1A57BF058265473,
    0x5649525455414C5F534E4F5330,
    0x2256B2,
    0x4272EA7D22D1B1E91D4D6EB1C55FCB5769B676DF746CF2FE77AF8FFFB86EEF2,
    0x6989A681C469D769F3A706C56550A63741A4B2D32BEF4B1209A26DAAD1DBB6,
    0x0,
]


@pytest.mark.asyncio
async def test_get_transaction_with_proof_facts(client_integration: FullNodeClient):
    transaction = await client_integration.get_transaction(
        tx_hash=INVOKE_WITH_PROOF_TX_HASH,
        response_flags=[TransactionResponseFlag.INCLUDE_PROOF_FACTS],
    )

    assert isinstance(transaction, InvokeTransactionV3)
    assert transaction.hash == INVOKE_WITH_PROOF_TX_HASH
    assert transaction.proof_facts == EXPECTED_PROOF_FACTS


@pytest.mark.asyncio
async def test_get_block_with_txs_response_flags(client_integration: FullNodeClient):
    receipt = await client_integration.get_transaction_receipt(
        tx_hash=INVOKE_WITH_PROOF_TX_HASH
    )

    block = await client_integration.get_block_with_txs(
        block_number=receipt.block_number,
        response_flags=[TransactionResponseFlag.INCLUDE_PROOF_FACTS],
    )

    assert block.block_number == receipt.block_number

    tx = block.transactions[0]
    assert isinstance(tx, InvokeTransactionV3)
    assert tx.proof_facts == EXPECTED_PROOF_FACTS


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
    assert len(block.transactions) == 1

    tx = block.transactions[0].transaction
    assert isinstance(tx, InvokeTransactionV3)
    assert tx.proof_facts == EXPECTED_PROOF_FACTS
