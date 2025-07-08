# pylint: disable=too-many-arguments
import dataclasses
import numbers
from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiohttp import ClientSession

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.hash.storage import get_storage_var_address
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    BlockStateUpdate,
    Call,
    ContractsStorageKeys,
    DAMode,
    DeclaredContractHash,
    DeclareTransactionV3,
    DeployAccountTransactionV3,
    EstimatedFee,
    ExecutionResources,
    FeePayment,
    InvokeTransactionV3,
    L1HandlerTransaction,
    MessageStatus,
    PriceUnit,
    ResourceBoundsMapping,
    SierraContractClass,
    SierraEntryPointsByType,
    StorageProofResponse,
    TransactionExecutionStatus,
    TransactionFinalityStatus,
    TransactionReceipt,
    TransactionStatus,
    TransactionStatusResponse,
    TransactionType,
)
from starknet_py.net.executable_models import (
    CasmClass,
    Deref,
    Immediate,
    TestLessThan,
    TestLessThanOrEqual,
)
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.http_client import RpcHttpClient
from starknet_py.net.models import DeclareV3
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.transaction_errors import (
    TransactionNotReceivedError,
    TransactionRevertedError,
)


@pytest.mark.asyncio
async def test_get_declare_transaction(
    client, declare_transaction_hash, class_hash, account
):
    transaction = await client.get_transaction(declare_transaction_hash)

    assert isinstance(transaction, DeclareTransactionV3)
    assert transaction.class_hash == class_hash
    assert transaction.hash == declare_transaction_hash
    assert transaction.sender_address == account.address


@pytest.mark.asyncio
async def test_get_invoke_transaction(
    client,
    invoke_transaction_hash,
):
    transaction = await client.get_transaction(invoke_transaction_hash)

    assert isinstance(transaction, InvokeTransactionV3)
    assert any(data == 1777 for data in transaction.calldata)
    assert transaction.hash == invoke_transaction_hash


@pytest.mark.asyncio
async def test_get_deploy_account_transaction(client, deploy_account_transaction_hash):
    transaction = await client.get_transaction(deploy_account_transaction_hash)

    assert isinstance(transaction, DeployAccountTransactionV3)
    assert transaction.hash == deploy_account_transaction_hash
    assert len(transaction.signature) > 0
    assert transaction.nonce == 0


@pytest.mark.asyncio
async def test_get_transaction_raises_on_not_received(client):
    with pytest.raises(
        TransactionNotReceivedError, match="Transaction was not received on Starknet."
    ):
        await client.get_transaction(tx_hash=0x9999)


@pytest.mark.asyncio
async def test_get_block_by_hash(
    client,
    block_with_declare_hash,
    block_with_declare_number,
):
    block = await client.get_block(block_hash=block_with_declare_hash)

    assert block.block_number == block_with_declare_number
    assert block.block_hash == block_with_declare_hash
    assert len(block.transactions) != 0


@pytest.mark.asyncio
async def test_get_block_by_number(
    client,
    block_with_declare_number,
    block_with_declare_hash,
):
    block = await client.get_block(block_number=block_with_declare_number)

    assert block.block_number == block_with_declare_number
    assert block.block_hash == block_with_declare_hash
    assert len(block.transactions) != 0


@pytest.mark.asyncio
async def test_get_storage_at(client, contract_address_2):
    storage = await client.get_storage_at(
        contract_address=contract_address_2,
        key=get_storage_var_address("balance"),
        block_hash="latest",
    )

    assert storage == 1777


@pytest.mark.asyncio
async def test_get_messages_status(client):
    with patch(
        f"{RpcHttpClient.__module__}.RpcHttpClient.call", AsyncMock()
    ) as mocked_message_status_call_rpc:
        return_value = [
            {
                "transaction_hash": "0x1",
                "finality_status": "ACCEPTED_ON_L2",
                "execution_status": "SUCCEEDED",
            },
            {
                "transaction_hash": "0x2",
                "finality_status": "ACCEPTED_ON_L2",
                "execution_status": "REVERTED",
                "failure_reason": "Some failure reason",
            },
        ]
        mocked_message_status_call_rpc.return_value = return_value

        messages_status = await client.get_messages_status(transaction_hash=0x1)

        assert all(isinstance(message, MessageStatus) for message in messages_status)

        assert messages_status[0].failure_reason is None
        assert messages_status[1].failure_reason == "Some failure reason"


@pytest.mark.asyncio
async def test_get_storage_proof(client):
    # Devnet doesn't support storage proofs, hence we need to use mock
    # https://github.com/0xSpaceShard/starknet-devnet/blob/27594f86b86ca227fe85784dba4a93ddfed9650b/tests/integration/general_rpc_tests.rs#L56

    with patch(
        f"{RpcHttpClient.__module__}.RpcHttpClient.call", AsyncMock()
    ) as mocked_message_status_call_rpc:
        return_value = {
            "id": 0,
            "jsonrpc": "2.0",
            "result": {
                "classes_proof": [
                    {"node": {"left": "0x123", "right": "0x123"}, "node_hash": "0x123"},
                    {
                        "node": {"child": "0x123", "length": 2, "path": "0x123"},
                        "node_hash": "0x123",
                    },
                ],
                "contracts_proof": {
                    "contract_leaves_data": [
                        {"class_hash": "0x123", "nonce": "0x0", "storage_root": "0x123"}
                    ],
                    "nodes": [
                        {
                            "node": {"left": "0x123", "right": "0x123"},
                            "node_hash": "0x123",
                        },
                        {
                            "node": {"child": "0x123", "length": 232, "path": "0x123"},
                            "node_hash": "0x123",
                        },
                    ],
                },
                "contracts_storage_proofs": [
                    [
                        {
                            "node": {"left": "0x123", "right": "0x123"},
                            "node_hash": "0x123",
                        },
                        {
                            "node": {"child": "0x123", "length": 123, "path": "0x123"},
                            "node_hash": "0x123",
                        },
                        {
                            "node": {"left": "0x123", "right": "0x123"},
                            "node_hash": "0x123",
                        },
                    ]
                ],
                "global_roots": {
                    "block_hash": "0x123",
                    "classes_tree_root": "0x456",
                    "contracts_tree_root": "0x789",
                },
            },
        }
        mocked_message_status_call_rpc.return_value = return_value["result"]

        storage_proof = await client.get_storage_proof(
            block_hash="latest",
            contract_addresses=[123],
            contracts_storage_keys=[
                ContractsStorageKeys(
                    contract_address=123,
                    storage_keys=[123],
                )
            ],
            class_hashes=[123],
        )

        assert isinstance(storage_proof, StorageProofResponse)
        assert len(storage_proof.classes_proof) == 2
        assert len(storage_proof.contracts_proof.nodes) == 2
        assert len(storage_proof.contracts_storage_proofs) == 1
        assert storage_proof.global_roots.block_hash == int("0x123", 16)
        assert storage_proof.global_roots.classes_tree_root == int("0x456", 16)
        assert storage_proof.global_roots.contracts_tree_root == int("0x789", 16)


@pytest.mark.asyncio
async def test_get_compiled_casm(client):
    strk_devnet_class_hash = (
        0x76791EF97C042F81FBF352AD95F39A22554EE8D7927B2CE3C681F3418B5206A
    )
    compiled_casm = await client.get_compiled_casm(class_hash=strk_devnet_class_hash)

    assert isinstance(compiled_casm, CasmClass)
    assert len(compiled_casm.bytecode) == 23286
    assert len(compiled_casm.hints) == 954

    first_hint = compiled_casm.hints[0][1][0]
    assert isinstance(first_hint, TestLessThanOrEqual)
    assert first_hint.test_less_than_or_equal.dst.offset == 0
    assert first_hint.test_less_than_or_equal.dst.register == "AP"
    assert isinstance(first_hint.test_less_than_or_equal.lhs, Immediate)
    assert first_hint.test_less_than_or_equal.lhs.immediate == 0
    assert isinstance(first_hint.test_less_than_or_equal.rhs, Deref)
    assert first_hint.test_less_than_or_equal.rhs.deref.offset == -6
    assert first_hint.test_less_than_or_equal.rhs.deref.register == "FP"

    second_hint = compiled_casm.hints[1][1][0]
    assert isinstance(second_hint, TestLessThan)
    assert isinstance(second_hint.test_less_than.lhs, Deref)
    assert second_hint.test_less_than.lhs.deref.register == "AP"
    assert second_hint.test_less_than.lhs.deref.offset == -2
    assert isinstance(second_hint.test_less_than.rhs, Immediate)
    assert (
        second_hint.test_less_than.rhs.immediate
        == 3618502788666131106986593281521497120414687020801267626233049500247285301248
    )
    assert second_hint.test_less_than.dst.register == "AP"
    assert second_hint.test_less_than.dst.offset == 4


@pytest.mark.asyncio
async def test_get_transaction_receipt(
    client, invoke_transaction_hash, block_with_invoke_number
):
    receipt = await client.get_transaction_receipt(tx_hash=invoke_transaction_hash)

    assert receipt.transaction_hash == invoke_transaction_hash
    assert receipt.block_number == block_with_invoke_number
    assert receipt.type == TransactionType.INVOKE


@pytest.mark.asyncio
async def test_estimate_fee_invoke_v3(account, contract_address):
    invoke_tx = await account.sign_invoke_v3(
        calls=Call(
            to_addr=contract_address,
            selector=get_selector_from_name("increase_balance"),
            calldata=[1000],
        ),
        resource_bounds=ResourceBoundsMapping.init_with_zeros(),
    )
    invoke_tx = await account.sign_for_fee_estimate(invoke_tx)
    estimated_fee = await account.client.estimate_fee(tx=invoke_tx)

    assert isinstance(estimated_fee, EstimatedFee)
    assert estimated_fee.unit == PriceUnit.FRI

    assert all(
        getattr(estimated_fee, field.name) >= 0
        for field in dataclasses.fields(EstimatedFee)
        if isinstance(getattr(estimated_fee, field.name), numbers.Number)
    )


@pytest.mark.asyncio
async def test_estimate_fee_declare_v3(
    account, abi_types_compiled_contract_and_class_hash
):
    declare_tx = await account.sign_declare_v3(
        compiled_contract=abi_types_compiled_contract_and_class_hash[0],
        compiled_class_hash=abi_types_compiled_contract_and_class_hash[1],
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    declare_tx = await account.sign_for_fee_estimate(declare_tx)
    estimated_fee = await account.client.estimate_fee(tx=declare_tx)

    assert isinstance(estimated_fee, EstimatedFee)
    assert estimated_fee.unit == PriceUnit.FRI

    assert all(
        getattr(estimated_fee, field.name) >= 0
        for field in dataclasses.fields(EstimatedFee)
        if isinstance(getattr(estimated_fee, field.name), numbers.Number)
    )


@pytest.mark.asyncio
async def test_estimate_fee_deploy_account(client, deploy_account_transaction):
    estimated_fee = await client.estimate_fee(tx=deploy_account_transaction)

    assert isinstance(estimated_fee, EstimatedFee)
    assert estimated_fee.unit == PriceUnit.FRI

    assert all(
        getattr(estimated_fee, field.name) >= 0
        for field in dataclasses.fields(EstimatedFee)
        if isinstance(getattr(estimated_fee, field.name), numbers.Number)
    )


@pytest.mark.asyncio
async def test_estimate_fee_for_multiple_transactions(
    client, deploy_account_transaction, contract_address, account
):
    invoke_tx = await account.sign_invoke_v3(
        calls=Call(
            to_addr=contract_address,
            selector=get_selector_from_name("increase_balance"),
            calldata=[1000],
        ),
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    invoke_tx = await account.sign_for_fee_estimate(invoke_tx)

    transactions = [invoke_tx, deploy_account_transaction]

    estimated_fees = await client.estimate_fee(tx=transactions, block_number="latest")

    assert isinstance(estimated_fees, list)

    for estimated_fee in estimated_fees:
        assert isinstance(estimated_fee, EstimatedFee)
        assert estimated_fee.unit == PriceUnit.FRI

        assert all(
            getattr(estimated_fee, field.name) >= 0
            for field in dataclasses.fields(EstimatedFee)
            if isinstance(getattr(estimated_fee, field.name), numbers.Number)
        )


@pytest.mark.asyncio
async def test_call_contract(client, contract_address_2):
    call = Call(
        to_addr=contract_address_2,
        selector=get_selector_from_name("get_balance"),
        calldata=[],
    )

    result = await client.call_contract(call, block_number="latest")

    assert result == [1777]


@pytest.mark.asyncio
async def test_add_transaction(map_contract, client, account):
    prepared_function_call = map_contract.functions["put"].prepare_invoke_v3(
        key=73, value=12
    )
    signed_invoke = await account.sign_invoke_v3(
        calls=prepared_function_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    result = await client.send_transaction(signed_invoke)
    await client.wait_for_tx(result.transaction_hash)
    transaction_receipt = await client.get_transaction_receipt(result.transaction_hash)

    assert transaction_receipt.execution_status == TransactionExecutionStatus.SUCCEEDED
    assert transaction_receipt.type == TransactionType.INVOKE


@pytest.mark.asyncio
async def test_add_invoke_v3_transaction_with_tip(map_contract, client, account):
    prepared_function_call = map_contract.functions["put"].prepare_invoke_v3(
        key=100, value=200
    )
    tip = 20000
    signed_invoke = await account.sign_invoke_v3(
        calls=prepared_function_call, resource_bounds=MAX_RESOURCE_BOUNDS, tip=tip
    )

    result = await client.send_transaction(signed_invoke)
    await client.wait_for_tx(result.transaction_hash)
    transaction_receipt = await client.get_transaction_receipt(result.transaction_hash)

    assert transaction_receipt.execution_status == TransactionExecutionStatus.SUCCEEDED
    assert transaction_receipt.type == TransactionType.INVOKE

    transaction = await client.get_transaction(result.transaction_hash)
    assert isinstance(transaction, InvokeTransactionV3)
    assert transaction.tip == tip


@pytest.mark.asyncio
async def test_add_declare_v3_transaction_with_tip(
    client, account, abi_types_compiled_contract_and_class_hash
):
    tip = 12345
    declare = await account.sign_declare_v3(
        compiled_contract=abi_types_compiled_contract_and_class_hash[0],
        compiled_class_hash=abi_types_compiled_contract_and_class_hash[1],
        resource_bounds=MAX_RESOURCE_BOUNDS,
        tip=tip,
    )
    result = await client.declare(declare)

    transaction = await client.get_transaction(result.transaction_hash)
    assert isinstance(transaction, DeclareTransactionV3)
    assert transaction.tip == tip


@pytest.mark.asyncio
async def test_get_class_hash_at(client, contract_address, class_hash):
    received_class_hash = await client.get_class_hash_at(
        contract_address=contract_address, block_hash="latest"
    )
    assert received_class_hash == class_hash


@pytest.mark.asyncio
async def test_get_class_by_hash(client, class_hash):
    contract_class = await client.get_class_by_hash(class_hash=class_hash)

    assert isinstance(contract_class, SierraContractClass)
    assert contract_class.sierra_program != ""
    assert contract_class.entry_points_by_type is not None
    assert contract_class.abi is not None


@pytest.mark.asyncio
async def test_wait_for_tx_accepted(client, get_tx_receipt_path, get_tx_status_path):
    with patch(
        get_tx_receipt_path,
        AsyncMock(),
    ) as mocked_receipt, patch(get_tx_status_path, AsyncMock()) as mocked_status:
        mocked_receipt.return_value = TransactionReceipt(
            transaction_hash=0x1,
            block_number=1,
            type=TransactionType.INVOKE,
            execution_status=TransactionExecutionStatus.SUCCEEDED,
            finality_status=TransactionFinalityStatus.ACCEPTED_ON_L2,
            execution_resources=Mock(spec=ExecutionResources),
            actual_fee=FeePayment(amount=1, unit=PriceUnit.WEI),
        )

        mocked_status.return_value = TransactionStatusResponse(
            finality_status=TransactionStatus.ACCEPTED_ON_L2,
        )

        tx_receipt = await client.wait_for_tx(tx_hash=0x1)
        assert tx_receipt.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2


@pytest.mark.asyncio
async def test_wait_for_tx_not_received(client, get_tx_status_path):
    exc_message = "Transaction not received."

    with patch(get_tx_status_path, AsyncMock()) as mocked_status:
        mocked_status.return_value = TransactionStatusResponse(
            finality_status=TransactionStatus.RECEIVED
        )

        with pytest.raises(TransactionNotReceivedError) as err:
            # We set `retries` to 1, otherwise `wait_for_tx` will try to fetch tx status until
            # it is either `ACCEPTED_ON_L2` or `ACCEPTED_ON_L1`
            await client.wait_for_tx(tx_hash=0x1, retries=1)

        assert exc_message in err.value.message


@pytest.mark.asyncio
async def test_wait_for_tx_reverted(client, get_tx_receipt_path, get_tx_status_path):
    exc_message = "Unknown Starknet error"

    with patch(
        get_tx_receipt_path,
        AsyncMock(),
    ) as mocked_receipt, patch(get_tx_status_path, AsyncMock()) as mocked_status:
        mocked_receipt.return_value = TransactionReceipt(
            transaction_hash=0x1,
            block_number=1,
            type=TransactionType.INVOKE,
            execution_status=TransactionExecutionStatus.REVERTED,
            finality_status=TransactionFinalityStatus.ACCEPTED_ON_L2,
            execution_resources=Mock(spec=ExecutionResources),
            revert_reason=exc_message,
            actual_fee=FeePayment(amount=1, unit=PriceUnit.WEI),
        )

        mocked_status.return_value = TransactionStatusResponse(
            finality_status=TransactionStatus.ACCEPTED_ON_L2,
        )

        with pytest.raises(TransactionRevertedError) as err:
            await client.wait_for_tx(tx_hash=0x1)

        assert exc_message in err.value.message


@pytest.mark.asyncio
async def test_wait_for_tx_unknown_error(
    client, get_tx_receipt_path, get_tx_status_path
):
    with patch(
        get_tx_receipt_path,
        AsyncMock(),
    ) as mocked_receipt, patch(get_tx_status_path, AsyncMock()) as mocked_status:
        mocked_receipt.side_effect = ClientError(message="Unknown error")
        mocked_status.return_value = TransactionStatusResponse(
            finality_status=TransactionStatus.ACCEPTED_ON_L2
        )

        with pytest.raises(ClientError, match="Unknown error"):
            await client.wait_for_tx(tx_hash="0x2137")


@pytest.mark.asyncio
async def test_custom_session_client(map_contract, devnet):
    # We must access protected `_client` to test session
    # pylint: disable=protected-access

    session = ClientSession()

    tx_hash = (
        await (
            await map_contract.functions["put"].invoke_v3(
                key=10, value=20, resource_bounds=MAX_RESOURCE_BOUNDS
            )
        ).wait_for_acceptance()
    ).hash

    client1 = FullNodeClient(node_url=devnet + "/rpc", session=session)
    client2 = FullNodeClient(node_url=devnet + "/rpc", session=session)
    internal_client1 = client1._client
    internal_client2 = client2._client

    assert internal_client1.session is not None
    assert internal_client1.session == session
    assert internal_client1.session.closed is False
    assert internal_client2.session is not None
    assert internal_client2.session == session
    assert internal_client2.session.closed is False

    response1 = await client1.get_transaction_receipt(tx_hash=tx_hash)
    response2 = await client2.get_transaction_receipt(tx_hash=tx_hash)
    assert response1 == response2

    assert internal_client1.session.closed is False
    assert internal_client2.session.closed is False

    await session.close()

    assert internal_client1.session.closed is True
    assert internal_client2.session.closed is True


@pytest.mark.asyncio
async def test_get_l1_handler_transaction(client):
    with patch(
        f"{RpcHttpClient.__module__}.RpcHttpClient.call", AsyncMock()
    ) as mocked_transaction_call_rpc:
        return_value = {
            "status": "ACCEPTED_ON_L1",
            "block_hash": "0x38ce7678420eaff5cd62597643ca515d0887579a8be69563067fe79a624592b",
            "block_number": 370459,
            "transaction_index": 9,
            "transaction": {
                "version": "0x0",
                "contract_address": "0x278f24c3e74cbf7a375ec099df306289beb0605a346277d200b791a7f811a19",
                "entry_point_selector": "0x2d757788a8d8d6f21d1cd40bce38a8222d70654214e96ff95d8086e684fbee5",
                "nonce": "0x34c20",
                "calldata": [
                    "0xd8beaa22894cd33f24075459cfba287a10a104e4",
                    "0x3f9c67ef1d31e24b386184b4ede63a869c4659de093ef437ee235cae4daf2be",
                    "0x3635c9adc5dea00000",
                    "0x0",
                    "0x7cb4539b69a2371f75d21160026b76a7a7c1cacb",
                ],
                "transaction_hash": "0x7e1ed66dbccf915857c6367fc641c24292c063e54a5dd55947c2d958d94e1a9",
                "type": "L1_HANDLER",
            },
        }
        mocked_transaction_call_rpc.return_value = return_value["transaction"]

        transaction = await client.get_transaction(tx_hash=0x1)

        assert isinstance(transaction, L1HandlerTransaction)
        assert transaction.nonce is not None
        assert transaction.nonce == 0x34C20


# TODO (#1219): investigate why test fails in batch but passes when single run
@pytest.mark.skip
@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_state_update_declared_contract_hashes(
    client,
    block_with_declare_number,
    class_hash,
):
    state_update = await client.get_state_update(block_number=block_with_declare_number)

    assert class_hash in state_update.state_diff.deprecated_declared_classes


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_state_update_storage_diffs(
    client,
    map_contract,
):
    resp = await map_contract.functions["put"].invoke_v3(
        key=10, value=20, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await resp.wait_for_acceptance()

    state_update = await client.get_state_update(block_number="latest")

    assert len(state_update.state_diff.storage_diffs) != 0
    assert isinstance(state_update, BlockStateUpdate)


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_state_update_deployed_contracts(
    class_hash,
    account,
):
    deployer = Deployer()
    contract_deployment = deployer.create_contract_deployment(class_hash=class_hash)
    deploy_invoke_tx = await account.sign_invoke_v3(
        contract_deployment.call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    resp = await account.client.send_transaction(deploy_invoke_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    state_update = await account.client.get_state_update(block_number="latest")

    assert len(state_update.state_diff.deployed_contracts) != 0
    assert isinstance(state_update, BlockStateUpdate)


@pytest.mark.asyncio
async def test_get_class_by_hash_sierra_program(client, hello_starknet_class_hash: int):
    contract_class = await client.get_class_by_hash(
        class_hash=hello_starknet_class_hash
    )

    assert isinstance(contract_class.parsed_abi, list)
    assert isinstance(contract_class, SierraContractClass)
    assert contract_class.contract_class_version == "0.1.0"
    assert isinstance(contract_class.sierra_program, list)
    assert isinstance(contract_class.entry_points_by_type, SierraEntryPointsByType)
    assert isinstance(contract_class.abi, str)


@pytest.mark.asyncio
async def test_get_declare_v3_transaction(
    client,
    hello_starknet_class_hash_tx_hash,
    declare_v3_hello_starknet: DeclareV3,
):
    (class_hash, tx_hash) = hello_starknet_class_hash_tx_hash

    transaction = await client.get_transaction(tx_hash=tx_hash)

    assert isinstance(transaction, DeclareTransactionV3)
    assert transaction == DeclareTransactionV3(
        class_hash=class_hash,
        compiled_class_hash=declare_v3_hello_starknet.compiled_class_hash,
        sender_address=declare_v3_hello_starknet.sender_address,
        hash=tx_hash,
        resource_bounds=declare_v3_hello_starknet.resource_bounds,
        signature=declare_v3_hello_starknet.signature,
        nonce=declare_v3_hello_starknet.nonce,
        version=declare_v3_hello_starknet.version,
        account_deployment_data=[],
        fee_data_availability_mode=DAMode.L1,
        nonce_data_availability_mode=DAMode.L1,
        paymaster_data=[],
        tip=0,
    )


@pytest.mark.asyncio
async def test_get_block_with_declare_v3(
    client,
    hello_starknet_class_hash_tx_hash,
    declare_v3_hello_starknet: DeclareV3,
    block_with_declare_v3_number: int,
):
    (class_hash, tx_hash) = hello_starknet_class_hash_tx_hash

    block = await client.get_block(block_number=block_with_declare_v3_number)

    assert (
        DeclareTransactionV3(
            class_hash=class_hash,
            compiled_class_hash=declare_v3_hello_starknet.compiled_class_hash,
            sender_address=declare_v3_hello_starknet.sender_address,
            hash=tx_hash,
            resource_bounds=declare_v3_hello_starknet.resource_bounds,
            signature=declare_v3_hello_starknet.signature,
            nonce=declare_v3_hello_starknet.nonce,
            version=declare_v3_hello_starknet.version,
            account_deployment_data=[],
            fee_data_availability_mode=DAMode.L1,
            nonce_data_availability_mode=DAMode.L1,
            paymaster_data=[],
            tip=0,
        )
        in block.transactions
    )


# TODO (#1219): add assert for replaced_class once it is fixed in devnet
@pytest.mark.asyncio
async def test_get_new_state_update(
    client,
    hello_starknet_class_hash: int,
    declare_v3_hello_starknet: DeclareV3,
    block_with_declare_v3_number: int,
):
    state_update_first = await client.get_state_update(
        block_number=block_with_declare_v3_number
    )
    assert state_update_first.state_diff.replaced_classes == []
    assert (
        DeclaredContractHash(
            class_hash=hello_starknet_class_hash,
            compiled_class_hash=declare_v3_hello_starknet.compiled_class_hash,
        )
        in state_update_first.state_diff.declared_classes
    )
