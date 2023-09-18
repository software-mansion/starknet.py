import pytest

from starknet_py.net.client_models import (
    DeclareTransaction,
    DeclareTransactionTrace,
    DeployAccountTransaction,
    DeployAccountTransactionTrace,
    InvokeTransaction,
    InvokeTransactionTrace,
    L1HandlerTransaction,
    L1HandlerTransactionTrace,
    RevertedFunctionInvocation,
    Transaction,
    TransactionTrace,
)

# TODO (#1179): move those tests to full_node_test.py


@pytest.mark.asyncio
async def test_trace_transaction(full_node_client_testnet):
    tx_to_trace: dict[type[Transaction], type[TransactionTrace]] = {
        InvokeTransaction: InvokeTransactionTrace,
        DeclareTransaction: DeclareTransactionTrace,
        DeployAccountTransaction: DeployAccountTransactionTrace,
        L1HandlerTransaction: L1HandlerTransactionTrace,
    }
    block = await full_node_client_testnet.get_block(block_number=600000)

    for tx in block.transactions:
        trace = await full_node_client_testnet.trace_transaction(tx_hash=tx.hash)
        tx = await full_node_client_testnet.get_transaction(tx_hash=tx.hash)
        assert tx_to_trace[type(tx)] == type(trace)


@pytest.mark.asyncio
async def test_trace_transaction_reverted(full_node_client_testnet):
    tx_hash = "0x604371f9414d26ad9e745301596de1d1219c1045f00c68d3be9bd195eb18632"
    trace = await full_node_client_testnet.trace_transaction(tx_hash=tx_hash)

    assert isinstance(trace.execute_invocation, RevertedFunctionInvocation)


@pytest.mark.asyncio
async def test_get_block_traces(full_node_client_testnet):
    # 800002 because I guess sometimes juno doesn't return valid transactions/parses input wrong
    block_number = 800006
    block_transaction_traces = await full_node_client_testnet.trace_block_transactions(
        block_number=block_number
    )
    block = await full_node_client_testnet.get_block(block_number=block_number)

    assert len(block_transaction_traces) == len(block.transactions)
    for i in range(0, len(block_transaction_traces)):
        assert (
            block_transaction_traces[i].transaction_hash == block.transactions[i].hash
        )


# TODO (#1169): remove this test?
@pytest.mark.asyncio
async def test_get_block_traces_warning_on_pending(full_node_client_testnet):
    with pytest.warns(
        UserWarning,
        match='Using "latest" block instead of "pending". "pending" blocks do not have a hash.',
    ):
        _ = await full_node_client_testnet.trace_block_transactions(
            block_number="pending"
        )
        _ = await full_node_client_testnet.trace_block_transactions(
            block_hash="pending"
        )
