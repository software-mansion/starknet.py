import pytest

from starknet_py.net.client_models import (
    DeclareTransactionTrace,
    DeclareTransactionV3,
    DeployAccountTransactionTrace,
    DeployAccountTransactionV3,
    InvokeTransactionTrace,
    InvokeTransactionV3,
    L1HandlerTransaction,
    L1HandlerTransactionTrace,
    RevertedFunctionInvocation,
)


@pytest.mark.asyncio
@pytest.mark.skip("TODO(#1562)")
async def test_trace_transaction_invoke_v3(client_sepolia_testnet):
    invoke_tx_hash = 0x26476DA48E56E5E7025543AD0BB9105DF00EE08571C6D17C4207462FF7717C4
    trace = await client_sepolia_testnet.trace_transaction(tx_hash=invoke_tx_hash)
    tx = await client_sepolia_testnet.get_transaction(tx_hash=invoke_tx_hash)

    assert isinstance(tx, InvokeTransactionV3)
    assert isinstance(trace, InvokeTransactionTrace)
    assert trace.execute_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
@pytest.mark.skip("TODO(#1562)")
async def test_trace_transaction_declare_v3(client_sepolia_testnet):
    declare_tx_hash = 0x6054540622D534FFFFB162A0E80C21BC106581EAFEB3EFAD29385B78E04983D
    trace = await client_sepolia_testnet.trace_transaction(tx_hash=declare_tx_hash)
    tx = await client_sepolia_testnet.get_transaction(tx_hash=declare_tx_hash)

    assert isinstance(tx, DeclareTransactionV3)
    assert isinstance(trace, DeclareTransactionTrace)
    assert trace.execution_resources is not None


@pytest.mark.asyncio
@pytest.mark.skip("TODO(#1562)")
async def test_trace_transaction_deploy_account_v3(client_sepolia_testnet):
    deploy_account_tx_hash = (
        0x06718B783A0B888F5421C4EB76A532FEB9FD5167B2B09274298F79798C782B32
    )
    trace = await client_sepolia_testnet.trace_transaction(
        tx_hash=deploy_account_tx_hash
    )
    tx = await client_sepolia_testnet.get_transaction(tx_hash=deploy_account_tx_hash)

    assert isinstance(tx, DeployAccountTransactionV3)
    assert isinstance(trace, DeployAccountTransactionTrace)
    assert trace.constructor_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
@pytest.mark.skip("TODO(#1562)")
async def test_trace_transaction_l1_handler(client_sepolia_testnet):
    l1_handler_tx_hash = (
        0x4C8C57B3AB646EF56AEF3DEF69A01BC86D049B98F25EBFE3699334D86C24D5
    )
    trace = await client_sepolia_testnet.trace_transaction(tx_hash=l1_handler_tx_hash)
    tx = await client_sepolia_testnet.get_transaction(tx_hash=l1_handler_tx_hash)

    assert isinstance(tx, L1HandlerTransaction)
    assert isinstance(trace, L1HandlerTransactionTrace)
    assert trace.function_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
@pytest.mark.skip("TODO(#1562)")
async def test_trace_transaction_reverted(client_sepolia_testnet):
    tx_hash = 0x00FECCA6A328DD11F40B79C30FE22D23BC6975D1A0923A95B90AFF4016A84333
    trace = await client_sepolia_testnet.trace_transaction(tx_hash=tx_hash)

    assert isinstance(trace.execute_invocation, RevertedFunctionInvocation)


@pytest.mark.asyncio
@pytest.mark.skip("TODO(#1562)")
async def test_get_block_traces(client_sepolia_testnet):
    block_number = 80000
    block_transaction_traces = await client_sepolia_testnet.trace_block_transactions(
        block_number=block_number
    )
    block = await client_sepolia_testnet.get_block(block_number=block_number)

    assert len(block_transaction_traces) == len(block.transactions)
    for i, block_transaction_trace in enumerate(block_transaction_traces):
        assert block_transaction_trace.transaction_hash == block.transactions[i].hash
