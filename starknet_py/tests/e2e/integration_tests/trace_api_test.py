from typing import Type

import pytest

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import InvokeTransaction, InvokeTransactionTrace, DeclareTransactionTrace, \
    DeclareTransaction, L1HandlerTransaction, L1HandlerTransactionTrace, DeployAccountTransaction, \
    DeployAccountTransactionTrace, Transaction, Call
from starknet_py.net.gateway_client import _get_payload
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_DIR
from starknet_py.tests.e2e.fixtures.misc import read_contract

tx_to_trace: dict[Type[Transaction]] = {
    InvokeTransaction: InvokeTransactionTrace,
    DeclareTransaction: DeclareTransactionTrace,
    DeployAccountTransaction: DeployAccountTransactionTrace,
    L1HandlerTransaction: L1HandlerTransactionTrace,
}


@pytest.mark.asyncio
async def test_trace_transaction(full_node_client_testnet):
    block = await full_node_client_testnet.get_block(block_number=800002)

    for tx in block.transactions:
        trace = await full_node_client_testnet.trace_transaction(tx_hash=tx.hash)
        tx = await full_node_client_testnet.get_transaction(tx_hash=tx.hash)
        assert tx_to_trace[type(tx)] == type(trace)


@pytest.mark.asyncio
async def test_get_block_traces(full_node_client_testnet):
    # 800002 because I guess sometimes juno doesn't return valid transactions/parses input wrong
    block_number = 800002
    block_transaction_traces = await full_node_client_testnet.get_block_traces(block_number=block_number)
    block = await full_node_client_testnet.get_block(block_number=block_number)

    assert len(block_transaction_traces) == len(block.transactions)
    for i in range(0, len(block_transaction_traces)):
        assert block_transaction_traces[i].transaction_hash == block.transactions[i].hash


@pytest.mark.asyncio
async def test_get_block_traces_warning_on_pending(full_node_client_testnet):
    with pytest.warns(
        UserWarning,
        match='Using "latest" block instead of "pending". "pending" blocks do not have a hash.'
    ):
        _ = await full_node_client_testnet.get_block_traces(block_number="pending")
        _ = await full_node_client_testnet.get_block_traces(block_hash="pending")
