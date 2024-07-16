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
)


@pytest.mark.asyncio
async def test_trace_transaction_invoke_v1(client_sepolia_testnet):
    invoke_tx_hash = 0x6D1938DC27FF335BA1D585B2FD78C12C30EF12A25E0DD64461ECD2089F5F839
    trace = await client_sepolia_testnet.trace_transaction(tx_hash=invoke_tx_hash)
    tx = await client_sepolia_testnet.get_transaction(tx_hash=invoke_tx_hash)
    assert type(tx) is InvokeTransactionV1
    assert type(trace) is InvokeTransactionTrace
    assert trace.execute_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_invoke_v3(client_sepolia_testnet):
    invoke_tx_hash = 0x26476DA48E56E5E7025543AD0BB9105DF00EE08571C6D17C4207462FF7717C4
    trace = await client_sepolia_testnet.trace_transaction(tx_hash=invoke_tx_hash)
    tx = await client_sepolia_testnet.get_transaction(tx_hash=invoke_tx_hash)
    assert type(tx) is InvokeTransactionV3
    assert type(trace) is InvokeTransactionTrace
    assert trace.execute_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_declare_v1(client_sepolia_testnet):
    declare_tx_hash = 0x5E27AAD6F9139F6EEB0EE886179C40B551E91AD8BCC80E16FF0FE6D5444D6F9
    trace = await client_sepolia_testnet.trace_transaction(tx_hash=declare_tx_hash)
    tx = await client_sepolia_testnet.get_transaction(tx_hash=declare_tx_hash)

    assert (type(tx)) is DeclareTransactionV1
    assert type(trace) is DeclareTransactionTrace
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_declare_v2(client_sepolia_testnet):
    declare_tx_hash = 0x1B8EA3EB7A4F6FAB922C91CF672F5881EE71F43C050BEFBA5629B22A6552F9B
    trace = await client_sepolia_testnet.trace_transaction(tx_hash=declare_tx_hash)
    tx = await client_sepolia_testnet.get_transaction(tx_hash=declare_tx_hash)

    assert (type(tx)) is DeclareTransactionV2
    assert type(trace) is DeclareTransactionTrace
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_declare_v3(client_sepolia_testnet):
    declare_tx_hash = 0x6054540622D534FFFFB162A0E80C21BC106581EAFEB3EFAD29385B78E04983D
    trace = await client_sepolia_testnet.trace_transaction(tx_hash=declare_tx_hash)
    tx = await client_sepolia_testnet.get_transaction(tx_hash=declare_tx_hash)

    assert (type(tx)) is DeclareTransactionV3
    assert type(trace) is DeclareTransactionTrace
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_deploy_account_v1(client_sepolia_testnet):
    deploy_account_tx_hash = (
        0x5943A2831021BF5A7EE732D1C0D572487013B9DB0A17481A46B3D9206BD5082
    )
    trace = await client_sepolia_testnet.trace_transaction(
        tx_hash=deploy_account_tx_hash
    )
    tx = await client_sepolia_testnet.get_transaction(tx_hash=deploy_account_tx_hash)

    assert (type(tx)) is DeployAccountTransactionV1
    assert type(trace) is DeployAccountTransactionTrace
    assert trace.constructor_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_deploy_account_v3(client_sepolia_testnet):
    deploy_account_tx_hash = (
        0x06718B783A0B888F5421C4EB76A532FEB9FD5167B2B09274298F79798C782B32
    )
    trace = await client_sepolia_testnet.trace_transaction(
        tx_hash=deploy_account_tx_hash
    )
    tx = await client_sepolia_testnet.get_transaction(tx_hash=deploy_account_tx_hash)

    assert (type(tx)) is DeployAccountTransactionV3
    assert type(trace) is DeployAccountTransactionTrace
    assert trace.constructor_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_l1_handler(client_sepolia_testnet):
    l1_handler_tx_hash = (
        0x4C8C57B3AB646EF56AEF3DEF69A01BC86D049B98F25EBFE3699334D86C24D5
    )
    trace = await client_sepolia_testnet.trace_transaction(tx_hash=l1_handler_tx_hash)
    tx = await client_sepolia_testnet.get_transaction(tx_hash=l1_handler_tx_hash)

    assert (type(tx)) is L1HandlerTransaction
    assert type(trace) is L1HandlerTransactionTrace
    assert trace.function_invocation is not None
    assert trace.execution_resources is not None


@pytest.mark.asyncio
async def test_trace_transaction_reverted(client_sepolia_testnet):
    tx_hash = 0x00FECCA6A328DD11F40B79C30FE22D23BC6975D1A0923A95B90AFF4016A84333
    trace = await client_sepolia_testnet.trace_transaction(tx_hash=tx_hash)

    assert isinstance(trace.execute_invocation, RevertedFunctionInvocation)


@pytest.mark.asyncio
async def test_get_block_traces(client_sepolia_testnet):
    block_number = 80000
    block_transaction_traces = await client_sepolia_testnet.trace_block_transactions(
        block_number=block_number
    )
    block = await client_sepolia_testnet.get_block(block_number=block_number)

    assert len(block_transaction_traces) == len(block.transactions)
    for i in range(len(block_transaction_traces)):
        assert (
            block_transaction_traces[i].transaction_hash == block.transactions[i].hash
        )
