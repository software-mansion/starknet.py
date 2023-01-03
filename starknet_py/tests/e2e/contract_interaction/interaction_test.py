import asyncio
from unittest.mock import MagicMock, patch

import pytest
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starkware_utils.error_handling import StarkErrorCode

from starknet_py.common import create_compiled_contract
from starknet_py.contract import Contract
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import Call, SentTransactionResponse
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.transaction_exceptions import (TransactionNotReceivedError,
                                                TransactionRejectedError)

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
async def test_wait_for_tx(account_client, map_contract):
    transaction = await map_contract.functions["put"].invoke(
        key=10, value=20, max_fee=MAX_FEE
    )
    await account_client.wait_for_tx(transaction.hash)


@pytest.mark.asyncio
async def test_wait_for_tx_throws_on_transaction_rejected(account_client, map_contract):
    invoke = map_contract.functions["put"].prepare(key=0x1, value=0x1, max_fee=MAX_FEE)

    # modify selector so that transaction will get rejected
    invoke.selector = 0x0123
    transaction = await invoke.invoke()

    with pytest.raises(TransactionRejectedError) as err:
        await account_client.wait_for_tx(transaction.hash)

    if isinstance(account_client.client, GatewayClient):
        assert "Entry point 0x123 not found in contract" in err.value.message


@pytest.mark.asyncio
async def test_warning_when_max_fee_equals_to_zero(map_contract):
    with pytest.warns(
        DeprecationWarning,
        match=r"Transaction will fail with max_fee set to 0. Change it to a higher value.",
    ):
        # try except have to be added because when running on a real environment it will throw an error (max_fee=0)
        try:
            await map_contract.functions["put"].invoke(10, 20, max_fee=0)
        except ClientError:
            pass


@pytest.mark.asyncio
async def test_transaction_not_received_error(map_contract):
    with patch(
        "starknet_py.net.account.account_client.AccountClient.send_transaction",
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
    contract = await Contract.from_address(map_contract.address, gateway_client)

    with pytest.raises(ValueError) as wrong_client_error:
        await contract.functions["put"].prepare(key=10, value=10).invoke(
            max_fee=MAX_FEE
        )

    assert (
        "Contract uses an account that can't invoke transactions. You need to use AccountClient for that."
        in str(wrong_client_error)
    )


@pytest.mark.asyncio
async def test_error_when_estimating_fee_while_not_using_account_client(
    gateway_client, map_contract
):
    contract = await Contract.from_address(map_contract.address, gateway_client)

    with pytest.raises(ValueError) as wrong_client_error:
        await contract.functions["put"].prepare(key=10, value=10).estimate_fee()

    assert (
        "Contract uses an account that can't invoke transactions. You need to use AccountClient for that."
        in str(wrong_client_error)
    )


@pytest.mark.asyncio
async def test_general_simplified_deployment_flow(
    new_account_client, map_compiled_contract
):
    declare_result = await Contract.declare(
        account=new_account_client,
        compiled_contract=map_compiled_contract,
        max_fee=MAX_FEE,
    )
    await declare_result.wait_for_acceptance()
    deployment = await declare_result.deploy(max_fee=MAX_FEE)
    await deployment.wait_for_acceptance()

    contract = deployment.deployed_contract

    assert isinstance(contract.address, int)
    assert len(contract.functions) != 0


@pytest.mark.asyncio
async def test_deploy_contract_flow(
    account_client, map_compiled_contract, map_class_hash
):
    abi = create_compiled_contract(compiled_contract=map_compiled_contract).abi

    deploy_result = await Contract.deploy_contract(
        class_hash=map_class_hash, account=account_client, abi=abi, max_fee=MAX_FEE
    )
    await deploy_result.wait_for_acceptance()

    contract = deploy_result.deployed_contract

    assert isinstance(contract.address, int)
    assert len(contract.functions) != 0
