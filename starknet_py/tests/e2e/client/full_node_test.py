import dataclasses
from unittest.mock import AsyncMock, patch

import pytest

from starknet_py.common import create_casm_class
from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.hash.storage import get_storage_var_address
from starknet_py.net.account.account import Account
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    BlockHashAndNumber,
    Call,
    ContractClass,
    DeclareTransaction,
    DeclareTransactionTrace,
    DeployAccountTransactionTrace,
    InvokeTransactionTrace,
    SierraContractClass,
    SimulatedTransaction,
    SyncStatus,
    TransactionType,
)
from starknet_py.net.full_node_client import _to_rpc_felt
from starknet_py.net.models import StarknetChainId
from starknet_py.tests.e2e.fixtures.constants import (
    CONTRACTS_COMPILED_V0_DIR,
    CONTRACTS_COMPILED_V1_DIR,
)
from starknet_py.tests.e2e.fixtures.misc import read_contract
from starknet_py.tests.e2e.utils import create_empty_block


def _parse_event_name(event: str) -> str:
    return _to_rpc_felt(get_selector_from_name(event))


FUNCTION_ONE_NAME = "put"
EVENT_ONE_PARSED_NAME = _parse_event_name("put_called")
FUNCTION_TWO_NAME = "another_put"
EVENT_TWO_PARSED_NAME = _parse_event_name("another_put_called")


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_node_get_declare_transaction_by_block_number_and_index(
    declare_transaction_hash, block_with_declare_number, full_node_client, class_hash
):
    tx = await full_node_client.get_transaction_by_block_id(
        block_number=block_with_declare_number, index=0
    )

    assert isinstance(tx, DeclareTransaction)
    assert tx.hash == declare_transaction_hash
    assert tx.class_hash == class_hash
    assert tx.version == 1


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_class_at(
    full_node_client, contract_address, hello_starknet_deploy_transaction_address
):
    declared_contract = await full_node_client.get_class_at(
        contract_address=contract_address, block_hash="latest"
    )

    assert isinstance(declared_contract, ContractClass)
    assert declared_contract.program != {}
    assert declared_contract.entry_points_by_type is not None
    assert declared_contract.abi is not None

    declared_contract = await full_node_client.get_class_at(
        contract_address=hello_starknet_deploy_transaction_address, block_hash="latest"
    )
    assert isinstance(declared_contract, SierraContractClass)
    assert declared_contract.sierra_program != {}
    assert declared_contract.entry_points_by_type is not None
    assert declared_contract.abi is not None


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_class_at_throws_on_wrong_address(full_node_client):
    with pytest.raises(
        ClientError, match="Client failed with code 20: Contract not found."
    ):
        await full_node_client.get_class_at(contract_address=0, block_hash="latest")


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_block_transaction_count(full_node_client):
    latest_block = await full_node_client.get_block("latest")

    for block_number in range(1, latest_block.block_number + 1):
        transaction_count = await full_node_client.get_block_transaction_count(
            block_number=block_number
        )

        assert transaction_count == 1


@pytest.mark.asyncio
async def test_method_raises_on_both_block_hash_and_number(full_node_client):
    with pytest.raises(
        ValueError,
        match="Arguments block_hash and block_number are mutually exclusive.",
    ):
        await full_node_client.get_block(block_number=0, block_hash="0x0")


@pytest.mark.asyncio
async def test_pending_transactions(full_node_client):
    with patch(
        "starknet_py.net.http_client.RpcHttpClient.call", AsyncMock()
    ) as mocked_http_call:
        mocked_http_call.return_value = [
            {
                "transaction_hash": "0x01",
                "class_hash": "0x05",
                "version": "0x0",
                "type": "DEPLOY",
                "contract_address": "0x02",
                "contract_address_salt": "0x0",
                "constructor_calldata": [],
            }
        ]

        pending_transactions = await full_node_client.get_pending_transactions()

    assert len(pending_transactions) == 1
    assert pending_transactions[0].hash == 0x1
    assert pending_transactions[0].signature == []
    assert pending_transactions[0].max_fee == 0


@pytest.mark.asyncio
async def test_get_transaction_receipt_deploy_account(
    full_node_client, deploy_account_details_factory
):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()
    deploy_result = await Account.deploy_account(
        address=address,
        class_hash=class_hash,
        salt=salt,
        key_pair=key_pair,
        client=full_node_client,
        chain=StarknetChainId.TESTNET,
        max_fee=int(1e16),
    )
    await deploy_result.wait_for_acceptance()

    receipt = await full_node_client.get_transaction_receipt(tx_hash=deploy_result.hash)
    assert receipt.type == TransactionType.DEPLOY_ACCOUNT
    assert receipt.contract_address == deploy_result.account.address


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_storage_at_incorrect_address_full_node_client(full_node_client):
    with pytest.raises(ClientError, match="Contract not found"):
        await full_node_client.get_storage_at(
            contract_address=0x1111,
            key=get_storage_var_address("balance"),
            block_hash="latest",
        )


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_without_following_continuation_token(
    full_node_client,
    simple_storage_with_event_contract: Contract,
):
    for i in range(4):
        await simple_storage_with_event_contract.functions[FUNCTION_ONE_NAME].invoke(
            i, i, auto_estimate=True
        )

    chunk_size = 3
    events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[[EVENT_ONE_PARSED_NAME]],
        follow_continuation_token=False,
        chunk_size=chunk_size,
    )

    assert len(events_response.events) == chunk_size
    assert events_response.continuation_token is not None


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_follow_continuation_token(
    full_node_client,
    simple_storage_with_event_contract: Contract,
):
    total_invokes = 2
    for i in range(total_invokes):
        await simple_storage_with_event_contract.functions[FUNCTION_ONE_NAME].invoke(
            i, i + 1, auto_estimate=True
        )

    events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[[EVENT_ONE_PARSED_NAME]],
        follow_continuation_token=True,
        chunk_size=1,
    )

    assert len(events_response.events) == total_invokes
    assert events_response.continuation_token is None


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_nonexistent_event_name(
    full_node_client,
    simple_storage_with_event_contract: Contract,
):
    await simple_storage_with_event_contract.functions[FUNCTION_ONE_NAME].invoke(
        1, 1, auto_estimate=True
    )

    events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[[_parse_event_name("nonexistent_event")]],
        follow_continuation_token=False,
        chunk_size=3,
    )

    assert len(events_response.events) == 0
    assert events_response.continuation_token is None


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_with_two_events(
    full_node_client,
    simple_storage_with_event_contract: Contract,
):
    invokes_of_one = 1
    invokes_of_two = 2
    invokes_of_all = invokes_of_one + invokes_of_two
    await simple_storage_with_event_contract.functions[FUNCTION_ONE_NAME].invoke(
        1, 2, auto_estimate=True
    )
    for i in range(invokes_of_two):
        await simple_storage_with_event_contract.functions[FUNCTION_TWO_NAME].invoke(
            i, i + 1, auto_estimate=True
        )

    event_one_events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[[EVENT_ONE_PARSED_NAME]],
        follow_continuation_token=True,
    )
    event_two_events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[[EVENT_TWO_PARSED_NAME]],
        follow_continuation_token=True,
    )
    event_one_two_events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[[int(EVENT_ONE_PARSED_NAME, 0), int(EVENT_TWO_PARSED_NAME, 0)]],
        follow_continuation_token=True,
    )

    assert len(event_one_events_response.events) == invokes_of_one
    assert event_one_events_response.continuation_token is None

    assert len(event_two_events_response.events) == invokes_of_two
    assert event_two_events_response.continuation_token is None

    assert len(event_one_two_events_response.events) == invokes_of_all
    assert event_one_two_events_response.continuation_token is None


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_start_from_continuation_token(
    full_node_client,
    simple_storage_with_event_contract: Contract,
):
    for i in range(5):
        await simple_storage_with_event_contract.functions[FUNCTION_ONE_NAME].invoke(
            i, i + 1, auto_estimate=True
        )

    chunk_size = 2
    continuation_token = "1"
    events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[[EVENT_ONE_PARSED_NAME]],
        continuation_token=continuation_token,
        chunk_size=chunk_size,
    )
    expected_continuation_token = str(int(continuation_token) + 1)

    assert len(events_response.events) == chunk_size
    assert events_response.continuation_token == expected_continuation_token


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_no_params(
    full_node_client,
    simple_storage_with_event_contract: Contract,
):
    default_chunk_size = 1
    for i in range(3):
        await simple_storage_with_event_contract.functions[FUNCTION_ONE_NAME].invoke(
            i, i + 1, auto_estimate=True
        )
        await simple_storage_with_event_contract.functions[FUNCTION_TWO_NAME].invoke(
            i, i + 1, auto_estimate=True
        )
    events_response = await full_node_client.get_events()

    assert len(events_response.events) == default_chunk_size


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_nonexistent_starting_block(
    full_node_client,
    simple_storage_with_event_contract: Contract,
):
    with pytest.raises(ClientError, match="Block not found"):
        await full_node_client.get_events(
            from_block_number=10000,
            to_block_hash="latest",
            address=simple_storage_with_event_contract.address,
            keys=[[EVENT_ONE_PARSED_NAME]],
            follow_continuation_token=False,
            chunk_size=1,
        )


@pytest.mark.asyncio
async def test_get_block_number(full_node_client):
    block_number = await full_node_client.get_block_number()

    # pylint: disable=protected-access
    await create_empty_block(full_node_client._client)

    new_block_number = await full_node_client.get_block_number()
    assert new_block_number == block_number + 1


@pytest.mark.asyncio
async def test_get_block_hash_and_number(full_node_client):
    block_hash_and_number = await full_node_client.get_block_hash_and_number()

    assert isinstance(block_hash_and_number, BlockHashAndNumber)

    # pylint: disable=protected-access
    await create_empty_block(full_node_client._client)

    new_block_hash_and_number = await full_node_client.get_block_hash_and_number()

    assert (
        new_block_hash_and_number.block_number == block_hash_and_number.block_number + 1
    )
    assert new_block_hash_and_number.block_hash > 0


@pytest.mark.asyncio
async def test_get_chain_id(full_node_client):
    chain_id = await full_node_client.get_chain_id()

    assert chain_id == hex(StarknetChainId.TESTNET.value)


@pytest.mark.asyncio
async def test_get_syncing_status_false(full_node_client):
    sync_status = await full_node_client.get_syncing_status()

    assert sync_status is False


@pytest.mark.asyncio
async def test_get_syncing_status(full_node_client):
    with patch(
        "starknet_py.net.http_client.RpcHttpClient.call", AsyncMock()
    ) as mocked_status:
        mocked_status.return_value = {
            "starting_block_num": "0xc8023",
            "current_block_num": "0xc9773",
            "highest_block_num": "0xc9773",
            "starting_block_hash": "0x60be3a55621597c15a53a1f83e977ca5e52e775ab2ebf572d2ebd6a8168fc88",
            "current_block_hash": "0x79abcb48e71524ad2e123624b0ee3d5f69f99759a23441f6f363794d0687a66",
            "highest_block_hash": "0x79abcb48e71524ad2e123624b0ee3d5f69f99759a23441f6f363794d0687a66",
        }

        sync_status = await full_node_client.get_syncing_status()

    assert isinstance(sync_status, SyncStatus)


# ---------------------------- Trace API tests ----------------------------


@pytest.mark.asyncio
async def test_simulate_transactions_skip_validate(
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
    invoke_tx = dataclasses.replace(invoke_tx, signature=[])

    simulated_txs = await full_node_account.client.simulate_transactions(
        transactions=[invoke_tx], skip_validate=True, block_number="latest"
    )
    assert simulated_txs[0].transaction_trace.validate_invocation is None

    with pytest.raises(ClientError, match=r".*INVALID_SIGNATURE_LENGTH.*"):
        _ = await full_node_account.client.simulate_transactions(
            transactions=[invoke_tx], block_number="latest"
        )


@pytest.mark.asyncio
async def test_simulate_transactions_skip_fee_charge(
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

    # TODO (#1179): change this test
    # because of python devnet, the SKIP_FEE_CHARGE flag isn't accepted
    with pytest.raises(ClientError, match=r".*SKIP_FEE_CHARGE.*"):
        _ = await full_node_account.client.simulate_transactions(
            transactions=[invoke_tx], skip_fee_charge=True, block_number="latest"
        )


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
    assert simulated_txs[0].transaction_trace.execute_invocation is not None

    invoke_tx = await full_node_account.sign_invoke_transaction(
        calls=[call, call], auto_estimate=True
    )
    simulated_txs = await full_node_account.client.simulate_transactions(
        transactions=[invoke_tx], block_number="latest"
    )

    assert isinstance(simulated_txs[0].transaction_trace, InvokeTransactionTrace)
    assert simulated_txs[0].transaction_trace.validate_invocation is not None
    assert simulated_txs[0].transaction_trace.execute_invocation is not None


@pytest.mark.asyncio
async def test_simulate_transactions_declare(full_node_account):
    compiled_contract = read_contract(
        "map_compiled.json", directory=CONTRACTS_COMPILED_V0_DIR
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
        # because raw calls do not increment nonce, it needs to be done manually
        nonce=invoke_tx.nonce + 1,
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
