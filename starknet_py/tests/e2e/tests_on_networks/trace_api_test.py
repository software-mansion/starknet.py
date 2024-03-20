import pytest

from starknet_py.net.client_models import (
    DeclareTransactionTrace,
    DeclareTransactionV1,
    DeclareTransactionV2,
    DeclareTransactionV3,
    DeployAccountTransactionTrace,
    DeployAccountTransactionV1,
    DeployAccountTransactionV3,
    InvokeTransactionTrace,
    InvokeTransactionV1,
    InvokeTransactionV3,
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
async def test_trace_transaction(client_sepolia_integration):
    tx_to_trace: dict[type[Transaction], type[TransactionTrace]] = {
        InvokeTransactionV1: InvokeTransactionTrace,
        InvokeTransactionV3: InvokeTransactionTrace,
        DeployAccountTransactionV1: DeployAccountTransactionTrace,
        L1HandlerTransaction: L1HandlerTransactionTrace,
    }
    block = await client_sepolia_integration.get_block(block_number=9708)

    for tx in block.transactions:
        trace = await client_sepolia_integration.trace_transaction(tx_hash=tx.hash)
        tx = await client_sepolia_integration.get_transaction(tx_hash=tx.hash)
        assert tx_to_trace[type(tx)] == type(trace)


@pytest.mark.asyncio
async def test_trace_transaction_invoke(client_sepolia_integration):
    invoke_tx_hash = 0x051506589B6D8900016B8E7362BDD07EE379F51127855DD0829E0768446C469C
    trace = await client_sepolia_integration.trace_transaction(tx_hash=invoke_tx_hash)

    assert type(trace) is InvokeTransactionTrace
    assert trace.execute_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_declare(client_sepolia_integration):
    declare_tx_hash = 0x0544A629990D2BED8CCF11910B30F2F1E18228ED5BE06660BEA20CAE13B2ACED
    trace = await client_sepolia_integration.trace_transaction(tx_hash=declare_tx_hash)

    assert type(trace) is DeclareTransactionTrace
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_deploy_account(client_sepolia_integration):
    deploy_account_tx_hash = (
        0x012DEBAE2435EA43C06610A31CCF8E7EA5DE9AEC43DAC7C7AA86905B4CCDEC49
    )
    trace = await client_sepolia_integration.trace_transaction(
        tx_hash=deploy_account_tx_hash
    )

    assert type(trace) is DeployAccountTransactionTrace
    assert trace.constructor_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_l1_handler(client_sepolia_integration):
    l1_handler_tx_hash = (
        0x07A00541410D41A98068D61905EB2440839A8BDD077BFB8B88C09478E3821CA6
    )
    trace = await client_sepolia_integration.trace_transaction(
        tx_hash=l1_handler_tx_hash
    )

    assert type(trace) is L1HandlerTransactionTrace
    assert trace.function_invocation is not None


@pytest.mark.asyncio
async def test_trace_transaction_reverted(client_sepolia_integration):
    tx_hash = 0x07DFF357E943748978B79DDD4A343A216F84B44154426CCB4CFD9C204858B15B
    trace = await client_sepolia_integration.trace_transaction(tx_hash=tx_hash)

    assert isinstance(trace.execute_invocation, RevertedFunctionInvocation)


@pytest.mark.asyncio
async def test_get_block_traces(client_sepolia_integration):
    block_number = 13001
    block_transaction_traces = (
        await client_sepolia_integration.trace_block_transactions(
            block_number=block_number
        )
    )
    block = await client_sepolia_integration.get_block(block_number=block_number)

    assert len(block_transaction_traces) == len(block.transactions)
    for i in range(len(block_transaction_traces)):
        assert (
            block_transaction_traces[i].transaction_hash == block.transactions[i].hash
        )


@pytest.mark.asyncio
async def test_simulate_transactions_declare_on_network(account_sepolia_integration):
    compiled_contract = read_contract(
        "map_compiled.json", directory=CONTRACTS_COMPILED_V0_DIR
    )
    declare_tx = await account_sepolia_integration.sign_declare_v1(
        compiled_contract, max_fee=int(1e16)
    )

    simulated_txs = await account_sepolia_integration.client.simulate_transactions(
        transactions=[declare_tx]
    )

    assert isinstance(simulated_txs[0].transaction_trace, DeclareTransactionTrace)
    assert simulated_txs[0].fee_estimation.overall_fee > 0
