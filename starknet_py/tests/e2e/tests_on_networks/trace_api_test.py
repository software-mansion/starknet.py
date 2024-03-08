import pytest

from starknet_py.net.client_models import (
    DeclareTransactionTrace,
    DeclareTransactionV1,
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
async def test_trace_transaction(client_goerli_integration):
    tx_to_trace: dict[type[Transaction], type[TransactionTrace]] = {
        InvokeTransactionV0: InvokeTransactionTrace,
        InvokeTransactionV1: InvokeTransactionTrace,
        DeclareTransactionV1: DeclareTransactionTrace,
        DeclareTransactionV2: DeclareTransactionTrace,
        DeployAccountTransactionV1: DeployAccountTransactionTrace,
        L1HandlerTransaction: L1HandlerTransactionTrace,
    }
    block = await client_goerli_integration.get_block(block_number=319080)

    for tx in block.transactions:
        trace = await client_goerli_integration.trace_transaction(tx_hash=tx.hash)
        tx = await client_goerli_integration.get_transaction(tx_hash=tx.hash)
        assert tx_to_trace[type(tx)] == type(trace)


@pytest.mark.asyncio
async def test_trace_transaction_invoke(client_goerli_integration):
    invoke_tx_hash = 0x05C3407F664E9A95A809FA0E0EB35C941863D280F30F73E292DA2F06779F7C59
    trace = await client_goerli_integration.trace_transaction(tx_hash=invoke_tx_hash)

    assert type(trace) is InvokeTransactionTrace
    assert trace.execute_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_declare(client_goerli_integration):
    declare_tx_hash = 0x05C2B2EE93E7BD33B911AFC822289EED2AE3A3B27CAECF92D7F793C5379C13D6
    trace = await client_goerli_integration.trace_transaction(tx_hash=declare_tx_hash)

    assert type(trace) is DeclareTransactionTrace
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_deploy_account(client_goerli_integration):
    deploy_account_tx_hash = (
        0x0270E24EA145B0A6022D0C50A97598B3BDCAB812BCCC24A97FFBB4365F90962C
    )
    trace = await client_goerli_integration.trace_transaction(
        tx_hash=deploy_account_tx_hash
    )

    assert type(trace) is DeployAccountTransactionTrace
    assert trace.constructor_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_l1_handler(client_goerli_integration):
    l1_handler_tx_hash = (
        0x04D54ACFEDB65334C2D8C4DB67E320E2ACA692412FD0E1311846FFCA568EFFAD
    )
    trace = await client_goerli_integration.trace_transaction(
        tx_hash=l1_handler_tx_hash
    )

    assert type(trace) is L1HandlerTransactionTrace
    assert trace.function_invocation is not None


@pytest.mark.asyncio
async def test_trace_transaction_reverted(client_goerli_integration):
    tx_hash = 0x0306673636C16CD3EC686EDCF24383D50099CD66C91CC89EC904AC8882BFB30C
    trace = await client_goerli_integration.trace_transaction(tx_hash=tx_hash)

    assert isinstance(trace.execute_invocation, RevertedFunctionInvocation)


@pytest.mark.asyncio
async def test_get_block_traces(client_goerli_integration):
    block_number = 329180
    block_transaction_traces = await client_goerli_integration.trace_block_transactions(
        block_number=block_number
    )
    block = await client_goerli_integration.get_block(block_number=block_number)

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
