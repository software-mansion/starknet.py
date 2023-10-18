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
async def test_trace_transaction_invoke(full_node_client_testnet):
    invoke_tx_hash = 0xdc6b381884866dd6c4accde75aa1fa7506e6b57612d3d3659f7b919ea07d7c
    trace = await full_node_client_testnet.trace_transaction(tx_hash=invoke_tx_hash)

    assert type(trace) == InvokeTransactionTrace
    assert trace.state_diff is not None


@pytest.mark.asyncio
async def test_trace_transaction_declare(full_node_client_testnet):
    declare_tx_hash = 0x62dd22627065568c6e4bd619c511217456b5a82acbdead7c3b5dfff92209451
    trace = await full_node_client_testnet.trace_transaction(tx_hash=declare_tx_hash)

    assert type(trace) == DeclareTransactionTrace
    assert trace.state_diff is not None


@pytest.mark.asyncio
async def test_trace_transaction_deploy_account(full_node_client_testnet):
    deploy_account_tx_hash = 0x7ad24e5d266ce371ec88c1ae537a92109e8af637c35673b6d459082431af7b
    trace = await full_node_client_testnet.trace_transaction(tx_hash=deploy_account_tx_hash)

    assert type(trace) == DeployAccountTransactionTrace
    assert trace.state_diff is not None


@pytest.mark.asyncio
async def test_trace_transaction_l1_handler(full_node_client_testnet):
    l1_handler_tx_hash = 0x6712d5cf540c1c2e51c03d6238f71cf86607f681669af586cd2eb8a92af68ac
    trace = await full_node_client_testnet.trace_transaction(tx_hash=l1_handler_tx_hash)

    assert type(trace) == L1HandlerTransactionTrace


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
    for i in range(len(block_transaction_traces)):
        assert (
            block_transaction_traces[i].transaction_hash == block.transactions[i].hash
        )
