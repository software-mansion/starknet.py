from typing import Type

import pytest

from starknet_py.common import create_casm_class
from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.client_models import (
    Call,
    DeclareTransaction,
    DeclareTransactionTrace,
    DeployAccountTransaction,
    DeployAccountTransactionTrace,
    InvokeTransaction,
    InvokeTransactionTrace,
    L1HandlerTransaction,
    L1HandlerTransactionTrace,
    SimulatedTransaction,
    Transaction,
    TransactionTrace,
)
from starknet_py.net.models import StarknetChainId
from starknet_py.tests.e2e.fixtures.constants import (
    CONTRACTS_COMPILED_DIR,
    CONTRACTS_COMPILED_V1_DIR,
)
from starknet_py.tests.e2e.fixtures.misc import read_contract

tx_to_trace: dict[type[Transaction], type[TransactionTrace]] = {
    InvokeTransaction: InvokeTransactionTrace,
    DeclareTransaction: DeclareTransactionTrace,
    DeployAccountTransaction: DeployAccountTransactionTrace,
    L1HandlerTransaction: L1HandlerTransactionTrace,
}


@pytest.mark.asyncio
async def test_trace_transaction(full_node_client_testnet):
    block = await full_node_client_testnet.get_block(block_number=600000)

    for tx in block.transactions:
        trace = await full_node_client_testnet.trace_transaction(tx_hash=tx.hash)
        tx = await full_node_client_testnet.get_transaction(tx_hash=tx.hash)
        assert tx_to_trace[type(tx)] == type(trace)


@pytest.mark.asyncio
async def test_simulate_transactions_flags(
    full_node_account, deployed_balance_contract
):
    assert isinstance(deployed_balance_contract, Contract)
    call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[0x10],
    )
    invoke_tx = await full_node_account.sign_invoke_transaction(
        calls=call, auto_estimate=True
    )

    simulated_txs = await full_node_account.client.simulate_transactions(
        transactions=[invoke_tx], skip_validate=True, block_number="latest"
    )

    assert simulated_txs[0].transaction_trace.validate_invocation is None


@pytest.mark.asyncio
async def test_simulate_transactions_invoke(
    full_node_account, deployed_balance_contract
):
    assert isinstance(deployed_balance_contract, Contract)
    call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[0x10],
    )
    invoke_tx = await full_node_account.sign_invoke_transaction(
        calls=call, auto_estimate=True
    )
    simulated_txs = await full_node_account.client.simulate_transactions(
        transactions=[invoke_tx], block_number="latest"
    )

    assert isinstance(simulated_txs[0], SimulatedTransaction)
    assert isinstance(simulated_txs[0].transaction_trace, InvokeTransactionTrace)
    assert simulated_txs[0].fee_estimation.overall_fee > 0
    assert simulated_txs[0].transaction_trace.validate_invocation is not None

    invoke_tx = await full_node_account.sign_invoke_transaction(
        calls=[call, call], auto_estimate=True
    )
    simulated_txs = await full_node_account.client.simulate_transactions(
        transactions=[invoke_tx], block_number="latest"
    )

    assert isinstance(simulated_txs[0].transaction_trace, InvokeTransactionTrace)
    assert simulated_txs[0].fee_estimation.overall_fee > 0
    assert simulated_txs[0].transaction_trace.validate_invocation is not None


@pytest.mark.asyncio
async def test_simulate_transactions_declare(full_node_account):
    compiled_contract = read_contract(
        "map_compiled.json", directory=CONTRACTS_COMPILED_DIR
    )
    declare_tx = await full_node_account.sign_declare_transaction(
        compiled_contract, max_fee=int(1e16)
    )

    simulated_txs = await full_node_account.client.simulate_transactions(
        transactions=[declare_tx], block_number="latest"
    )

    assert isinstance(simulated_txs[0].transaction_trace, DeclareTransactionTrace)
    assert simulated_txs[0].fee_estimation.overall_fee > 0
    assert simulated_txs[0].transaction_trace.validate_invocation is not None


@pytest.mark.asyncio
async def test_simulate_transactions_two_txs(
    full_node_account, deployed_balance_contract
):
    assert isinstance(deployed_balance_contract, Contract)
    call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[0x10],
    )
    invoke_tx = await full_node_account.sign_invoke_transaction(
        calls=call, auto_estimate=True
    )

    compiled_v2_contract = read_contract(
        "test_contract_declare_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    compiled_v2_contract_casm = read_contract(
        "test_contract_declare_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
    )
    casm_class = create_casm_class(compiled_v2_contract_casm)
    casm_class_hash = compute_casm_class_hash(casm_class)

    declare_v2_tx = await full_node_account.sign_declare_v2_transaction(
        compiled_contract=compiled_v2_contract,
        compiled_class_hash=casm_class_hash,
        nonce=invoke_tx.nonce
        + 1,  # because raw calls do not increment nonce, it needs to be done manually
        max_fee=int(1e16),
    )

    simulated_txs = await full_node_account.client.simulate_transactions(
        transactions=[invoke_tx, declare_v2_tx], block_number="latest"
    )

    assert isinstance(simulated_txs[0].transaction_trace, InvokeTransactionTrace)
    assert simulated_txs[0].fee_estimation.overall_fee > 0
    assert simulated_txs[0].transaction_trace.validate_invocation is not None
    assert simulated_txs[0].transaction_trace.execute_invocation is not None

    assert isinstance(simulated_txs[1].transaction_trace, DeclareTransactionTrace)
    assert simulated_txs[1].fee_estimation.overall_fee > 0
    assert simulated_txs[1].transaction_trace.validate_invocation is not None


@pytest.mark.asyncio
async def test_simulate_transactions_deploy_account(
    full_node_client, deploy_account_details_factory
):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()
    address = compute_address(
        salt=salt,
        class_hash=class_hash,
        constructor_calldata=[key_pair.public_key],
        deployer_address=0,
    )
    account = Account(
        address=address,
        client=full_node_client,
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
    )
    deploy_account_tx = await account.sign_deploy_account_transaction(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=[key_pair.public_key],
        max_fee=int(1e16),
    )

    simulated_txs = await full_node_client.simulate_transactions(
        transactions=[deploy_account_tx], block_number="latest"
    )

    assert isinstance(simulated_txs[0].transaction_trace, DeployAccountTransactionTrace)
    assert simulated_txs[0].fee_estimation.overall_fee > 0
    assert simulated_txs[0].transaction_trace.constructor_invocation is not None


@pytest.mark.asyncio
async def test_get_block_traces(full_node_client_testnet):
    # 800002 because I guess sometimes juno doesn't return valid transactions/parses input wrong
    block_number = 800002
    block_transaction_traces = await full_node_client_testnet.get_block_traces(
        block_number=block_number
    )
    block = await full_node_client_testnet.get_block(block_number=block_number)

    assert len(block_transaction_traces) == len(block.transactions)
    for i in range(0, len(block_transaction_traces)):
        assert (
            block_transaction_traces[i].transaction_hash == block.transactions[i].hash
        )


@pytest.mark.asyncio
async def test_get_block_traces_warning_on_pending(full_node_client_testnet):
    with pytest.warns(
        UserWarning,
        match='Using "latest" block instead of "pending". "pending" blocks do not have a hash.',
    ):
        _ = await full_node_client_testnet.get_block_traces(block_number="pending")
        _ = await full_node_client_testnet.get_block_traces(block_hash="pending")
