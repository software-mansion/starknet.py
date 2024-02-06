import pytest

from starknet_py.net.client_models import (
    DeclareTransactionTrace,
    DeclareTransactionV2,
    DeployAccountTransactionTrace,
    DeployAccountTransactionV1,
    InvokeTransactionTrace,
    InvokeTransactionV0,
    InvokeTransactionV1,
    L1HandlerTransaction,
    L1HandlerTransactionTrace,
    RevertedFunctionInvocation,
    Transaction,
    TransactionTrace,
)
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V0_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract

# TODO (#1219): move those tests to full_node_test.py


@pytest.mark.asyncio
async def test_trace_transaction(client_goerli_testnet):
    tx_to_trace: dict[type[Transaction], type[TransactionTrace]] = {
        InvokeTransactionV0: InvokeTransactionTrace,
        InvokeTransactionV1: InvokeTransactionTrace,
        DeclareTransactionV2: DeclareTransactionTrace,
        DeployAccountTransactionV1: DeployAccountTransactionTrace,
        L1HandlerTransaction: L1HandlerTransactionTrace,
    }
    block = await client_goerli_testnet.get_block(block_number=600000)

    for tx in block.transactions:
        trace = await client_goerli_testnet.trace_transaction(tx_hash=tx.hash)
        tx = await client_goerli_testnet.get_transaction(tx_hash=tx.hash)
        assert tx_to_trace[type(tx)] == type(trace)


@pytest.mark.asyncio
async def test_trace_transaction_invoke(client_goerli_testnet):
    invoke_tx_hash = 0xDC6B381884866DD6C4ACCDE75AA1FA7506E6B57612D3D3659F7B919EA07D7C
    trace = await client_goerli_testnet.trace_transaction(tx_hash=invoke_tx_hash)

    assert type(trace) is InvokeTransactionTrace
    assert trace.execute_invocation is not None


@pytest.mark.asyncio
async def test_trace_transaction_declare(client_goerli_testnet):
    declare_tx_hash = 0x62DD22627065568C6E4BD619C511217456B5A82ACBDEAD7C3B5DFFF92209451
    trace = await client_goerli_testnet.trace_transaction(tx_hash=declare_tx_hash)

    assert type(trace) is DeclareTransactionTrace


@pytest.mark.asyncio
async def test_trace_transaction_deploy_account(client_goerli_testnet):
    deploy_account_tx_hash = (
        0x7AD24E5D266CE371EC88C1AE537A92109E8AF637C35673B6D459082431AF7B
    )
    trace = await client_goerli_testnet.trace_transaction(
        tx_hash=deploy_account_tx_hash
    )

    assert type(trace) is DeployAccountTransactionTrace
    assert trace.constructor_invocation is not None


@pytest.mark.asyncio
async def test_trace_transaction_l1_handler(client_goerli_testnet):
    l1_handler_tx_hash = (
        0x6712D5CF540C1C2E51C03D6238F71CF86607F681669AF586CD2EB8A92AF68AC
    )
    trace = await client_goerli_testnet.trace_transaction(tx_hash=l1_handler_tx_hash)

    assert type(trace) is L1HandlerTransactionTrace
    assert trace.function_invocation is not None


@pytest.mark.asyncio
async def test_trace_transaction_reverted(client_goerli_testnet):
    tx_hash = "0x604371f9414d26ad9e745301596de1d1219c1045f00c68d3be9bd195eb18632"
    trace = await client_goerli_testnet.trace_transaction(tx_hash=tx_hash)

    assert isinstance(trace.execute_invocation, RevertedFunctionInvocation)


@pytest.mark.asyncio
async def test_get_block_traces(client_goerli_testnet):
    # 800002 because I guess sometimes juno doesn't return valid transactions/parses input wrong
    block_number = 800006
    block_transaction_traces = await client_goerli_testnet.trace_block_transactions(
        block_number=block_number
    )
    block = await client_goerli_testnet.get_block(block_number=block_number)

    assert len(block_transaction_traces) == len(block.transactions)
    for i in range(len(block_transaction_traces)):
        assert (
            block_transaction_traces[i].transaction_hash == block.transactions[i].hash
        )


@pytest.mark.asyncio
async def test_simulate_transactions_declare_on_network(account_goerli_testnet):
    compiled_contract = read_contract(
        "map_compiled.json", directory=CONTRACTS_COMPILED_V0_DIR
    )
    declare_tx = await account_goerli_testnet.sign_declare_v1(
        compiled_contract, max_fee=int(1e16)
    )

    simulated_txs = await account_goerli_testnet.client.simulate_transactions(
        transactions=[declare_tx]
    )

    assert isinstance(simulated_txs[0].transaction_trace, DeclareTransactionTrace)
    assert simulated_txs[0].fee_estimation.overall_fee > 0
