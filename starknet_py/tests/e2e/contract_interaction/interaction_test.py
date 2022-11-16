import asyncio
from unittest.mock import patch, MagicMock

import pytest
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starkware_utils.error_handling import StarkErrorCode

from starknet_py.net.client_models import SentTransactionResponse, Call
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_DIR
from starknet_py.tests.e2e.utils import deploy
from starknet_py.transaction_exceptions import (
    TransactionRejectedError,
    TransactionNotReceivedError,
)
from starknet_py.contract import Contract
from starknet_py.net.client_errors import ClientError, ContractNotFoundError

MAX_FEE = int(1e20)


@pytest.mark.asyncio
async def test_max_fee_is_set_in_sent_invoke(map_contract):
    key = 2
    value = 3

    prepared_call = map_contract.functions["put"].prepare(key, value, max_fee=100)
    assert prepared_call.max_fee == 100
    invocation = await prepared_call.invoke()
    assert invocation.invoke_transaction.max_fee == 100

    invocation = await map_contract.functions["put"].invoke(key, value, max_fee=200)
    assert invocation.invoke_transaction.max_fee == 200

    prepared_call = map_contract.functions["put"].prepare(key, value, max_fee=300)
    assert prepared_call.max_fee == 300
    invocation = await prepared_call.invoke(max_fee=400)
    assert invocation.invoke_transaction.max_fee == 400


@pytest.mark.asyncio
async def test_auto_fee_estimation(map_contract):
    key = 2
    value = 3

    prepared_call = map_contract.functions["put"].prepare(key, value)
    invocation = await prepared_call.invoke(auto_estimate=True)

    assert invocation.invoke_transaction.max_fee is not None


@pytest.mark.asyncio
async def test_throws_on_estimate_with_positive_max_fee(map_contract):
    key = 2
    value = 3

    prepared_call = map_contract.functions["put"].prepare(key, value, max_fee=100)
    with pytest.raises(ValueError) as exinfo:
        await prepared_call.estimate_fee()

    assert (
        "Cannot estimate fee of PreparedFunctionCall with max_fee not None or 0."
        in str(exinfo.value)
    )


@pytest.mark.asyncio
async def test_throws_on_both_max_fee_and_auto_estimate(map_contract):
    key = 2
    value = 3

    invocation = map_contract.functions["put"].prepare(key, value)
    with pytest.raises(ValueError) as exinfo:
        await invocation.invoke(max_fee=10, auto_estimate=True)

    assert (
        "Max_fee and auto_estimate are exclusive and cannot be provided at the same time."
        in str(exinfo.value)
    )


@pytest.mark.asyncio
async def test_throws_on_both_max_fee_in_prepare_and_auto_estimate(map_contract):
    key = 2
    value = 3

    invocation = map_contract.functions["put"].prepare(key, value, max_fee=2000)
    with pytest.raises(ValueError) as exinfo:
        await invocation.invoke(auto_estimate=True)

    assert (
        "Max_fee and auto_estimate are exclusive and cannot be provided at the same time."
        in str(exinfo.value)
    )


@pytest.mark.asyncio
async def test_throws_on_call_without_max_fee(map_contract):
    key = 2
    value = 3

    with pytest.raises(ValueError) as exinfo:
        await map_contract.functions["put"].invoke(key, value)

    assert "Max_fee must be specified when invoking a transaction" in str(exinfo.value)


@pytest.mark.asyncio
async def test_throws_on_prepared_call_without_max_fee(map_contract):
    key = 2
    value = 3

    prepared_call = map_contract.functions["put"].prepare(key, value)

    with pytest.raises(ValueError) as exinfo:
        await prepared_call.invoke()

    assert "Max_fee must be specified when invoking a transaction" in str(exinfo.value)


@pytest.mark.asyncio
async def test_latest_max_fee_takes_precedence(map_contract):
    key = 2
    value = 3

    prepared_function = map_contract.functions["put"].prepare(key, value, max_fee=20)
    invocation = await prepared_function.invoke(max_fee=50)

    assert invocation.invoke_transaction.max_fee == 50


@pytest.mark.asyncio
async def test_prepare_without_max_fee(map_contract):
    key = 2
    value = 3

    prepared_call = map_contract.functions["put"].prepare(key, value)

    assert prepared_call.max_fee is None


@pytest.mark.asyncio
@pytest.mark.parametrize("key, value", ((2, 13), (412312, 32134), (12345, 3567)))
async def test_invoke_and_call(key, value, map_contract):

    invocation = await map_contract.functions["put"].invoke(key, value, max_fee=MAX_FEE)
    await invocation.wait_for_acceptance(wait_for_accept=True)
    (response,) = await map_contract.functions["get"].call(key)

    assert response == value


user_auth_source = (CONTRACTS_DIR / "user_auth.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_get_code_not_found(new_account):
    with pytest.raises(ContractNotFoundError) as exinfo:
        await Contract.from_address(1, account=new_account)

    assert "No contract found" in str(exinfo.value)


@pytest.mark.asyncio
async def test_call_uninitialized_contract(gateway_account_client):
    with pytest.raises(ClientError) as err:
        await gateway_account_client.call_contract(
            Call(
                to_addr=1,
                selector=get_selector_from_name("get_nonce"),
                calldata=[],
            ),
            block_hash="latest",
        )

    assert "500" in str(err.value)
    assert "Requested contract address 0x1 is not deployed." in err.value.message


@pytest.mark.asyncio
async def test_wait_for_tx(account, map_source_code):
    deployment = await deploy(
        compilation_source=map_source_code,
        account=account,
    )
    await account.client.wait_for_tx(deployment.hash)


@pytest.mark.asyncio
async def test_wait_for_tx_throws_on_transaction_rejected(account, map_contract):
    invoke = map_contract.functions["put"].prepare(key=0x1, value=0x1, max_fee=MAX_FEE)

    # modify selector so that transaction will get rejected
    invoke.selector = 0x0123
    transaction = await invoke.invoke()

    with pytest.raises(TransactionRejectedError) as err:
        await account.client.wait_for_tx(transaction.hash)

    if isinstance(account.client, GatewayClient):
        assert "Entry point 0x123 not found in contract" in err.value.message


@pytest.mark.asyncio
async def test_transaction_not_received_error(map_contract):
    with patch(
        "starknet_py.net.gateway_client.GatewayClient.send_transaction",
        MagicMock(),
    ) as mocked_send_transaction:
        result = asyncio.Future()
        result.set_result(
            SentTransactionResponse(
                code=StarkErrorCode.TRANSACTION_CANCELLED.value, transaction_hash=0x123
            )
        )

        mocked_send_transaction.return_value = result

        with pytest.raises(TransactionNotReceivedError) as tx_not_received:
            result = await map_contract.functions["put"].invoke(10, 20, max_fee=MAX_FEE)
            await result.wait_for_acceptance()

        assert "Transaction not received" == tx_not_received.value.message


@pytest.mark.asyncio
async def test_error_when_invoking_without_account_client(gateway_client, map_contract):
    contract = await Contract.from_address(map_contract.address, client=gateway_client)

    with pytest.raises(ValueError) as wrong_client_error:
        await contract.functions["put"].prepare(key=10, value=10).invoke(
            max_fee=MAX_FEE
        )

    assert (
        "Contract was created without Account provided or with Client that is not an account."
        in str(wrong_client_error)
    )


@pytest.mark.asyncio
async def test_error_when_estimating_fee_while_not_using_account_client(
    gateway_client, map_contract
):
    contract = await Contract.from_address(map_contract.address, client=gateway_client)

    with pytest.raises(ValueError) as wrong_client_error:
        await contract.functions["put"].prepare(key=10, value=10).estimate_fee()

    assert (
        "Contract was created without Account provided or with Client that is not an account."
        in str(wrong_client_error)
    )


@pytest.mark.asyncio
async def test_constructor_arguments():
    value = 10
    tuple_value = (1, (2, 3))
    arr = [1, 2, 3]
    struct = {"value": 12, "nested_struct": {"value": 99}}

    constructor_with_arguments_source = (
        CONTRACTS_DIR / "constructor_with_arguments.cairo"
    ).read_text("utf-8")

    # Contract should throw if constructor arguments were not provided
    with pytest.raises(ValueError) as err:
        Contract.compute_address(
            compilation_source=constructor_with_arguments_source,
            salt=1234,
        )

    assert "no args were provided" in str(err.value)

    # Positional params
    address1 = Contract.compute_address(
        compilation_source=constructor_with_arguments_source,
        constructor_args=[value, tuple_value, arr, struct],
        salt=1234,
    )
    assert address1

    # Named params
    address2 = Contract.compute_address(
        compilation_source=constructor_with_arguments_source,
        constructor_args={
            "single_value": value,
            "tuple": tuple_value,
            "arr": arr,
            "dict": struct,
        },
        salt=1234,
    )
    assert address2


@pytest.mark.asyncio
async def test_constructor_without_arguments():
    constructor_without_arguments_source = (
        CONTRACTS_DIR / "constructor_without_arguments.cairo"
    ).read_text("utf-8")

    assert Contract.compute_address(
        compilation_source=constructor_without_arguments_source,
        salt=1234,
    )
