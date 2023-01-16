from unittest.mock import AsyncMock, patch

import pytest
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starkware_utils.error_handling import StarkErrorCode

from starknet_py.common import create_compiled_contract
from starknet_py.contract import Contract
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import Call, SentTransactionResponse
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.transaction_exceptions import (
    TransactionNotReceivedError,
    TransactionRejectedError,
)

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
async def test_throws_invoke_without_max_fee(map_contract):
    error_message = "Argument max_fee must be specified when invoking a transaction."

    with pytest.raises(ValueError, match=error_message):
        await map_contract.functions["put"].invoke(2, 3)


@pytest.mark.asyncio
async def test_throws_prepared_call_invoke_without_max_fee(map_contract):
    error_message = "Argument max_fee must be specified when invoking a transaction."

    prepared_call = map_contract.functions["put"].prepare(2, 3)
    with pytest.raises(ValueError, match=error_message):
        await prepared_call.invoke()


@pytest.mark.asyncio
async def test_throws_prepared_call_with_max_fee_invoke_with_auto_estimate(
    map_contract,
):
    error_message = "Arguments max_fee and auto_estimate are mutually exclusive."

    invocation = map_contract.functions["put"].prepare(2, 3, max_fee=2000)
    with pytest.raises(ValueError, match=error_message):
        await invocation.invoke(auto_estimate=True)


@pytest.mark.asyncio
async def test_throws_on_call_without_max_fee(map_contract):
    error_message = "Arguments max_fee and auto_estimate are mutually exclusive."

    prepared_call = map_contract.functions["put"].prepare(2, 3)
    with pytest.raises(ValueError, match=error_message):
        await prepared_call.invoke(max_fee=10, auto_estimate=True)


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
async def test_call_uninitialized_contract(gateway_client):
    with pytest.raises(
        ClientError, match="Requested contract address 0x1 is not deployed."
    ) as err:
        await gateway_client.call_contract(
            Call(
                to_addr=1,
                selector=get_selector_from_name("get_nonce"),
                calldata=[],
            ),
            block_hash="latest",
        )

    assert "500" in str(err.value)


@pytest.mark.asyncio
async def test_wait_for_tx(client, map_contract):
    transaction = await map_contract.functions["put"].invoke(
        key=10, value=20, max_fee=MAX_FEE
    )
    await client.wait_for_tx(transaction.hash)


@pytest.mark.asyncio
async def test_wait_for_tx_throws_on_transaction_rejected(client, map_contract):
    invoke = map_contract.functions["put"].prepare(key=0x1, value=0x1, max_fee=MAX_FEE)

    # modify selector so that transaction will get rejected
    invoke.selector = 0x0123
    transaction = await invoke.invoke()

    with pytest.raises(TransactionRejectedError) as err:
        await client.wait_for_tx(transaction.hash)

    if isinstance(client, GatewayClient):
        assert "Entry point 0x123 not found in contract" in err.value.message


@pytest.mark.asyncio
async def test_transaction_not_received_error(map_contract):
    with patch(
        "starknet_py.net.gateway_client.GatewayClient.send_transaction",
        AsyncMock(),
    ) as mocked_send_transaction:
        mocked_send_transaction.return_value = SentTransactionResponse(
            code=StarkErrorCode.TRANSACTION_CANCELLED.value, transaction_hash=0x123
        )

        with pytest.raises(
            TransactionNotReceivedError, match="Transaction was not received"
        ):
            result = await map_contract.functions["put"].invoke(10, 20, max_fee=MAX_FEE)
            await result.wait_for_acceptance()


@pytest.mark.asyncio
async def test_error_when_invoking_without_account(gateway_client, map_contract):
    contract = await Contract.from_address(map_contract.address, gateway_client)

    with pytest.raises(
        ValueError,
        match="Contract was created without Account or with Client that is not an account.",
    ):
        await contract.functions["put"].prepare(key=10, value=10).invoke(
            max_fee=MAX_FEE
        )


@pytest.mark.asyncio
async def test_error_when_estimating_fee_while_not_using_account(
    gateway_client, map_contract
):
    contract = await Contract.from_address(map_contract.address, gateway_client)

    with pytest.raises(
        ValueError,
        match="Contract was created without Account or with Client that is not an account.",
    ):
        await contract.functions["put"].prepare(key=10, value=10).estimate_fee()


@pytest.mark.asyncio
async def test_general_simplified_deployment_flow(account, map_compiled_contract):
    declare_result = await Contract.declare(
        account=account,
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
async def test_deploy_contract_flow(account, map_compiled_contract, map_class_hash):
    abi = create_compiled_contract(compiled_contract=map_compiled_contract).abi

    deploy_result = await Contract.deploy_contract(
        class_hash=map_class_hash, account=account, abi=abi, max_fee=MAX_FEE
    )
    await deploy_result.wait_for_acceptance()

    contract = deploy_result.deployed_contract

    assert isinstance(contract.address, int)
    assert len(contract.functions) != 0


def test_contract_raises_on_both_client_and_account(gateway_client, gateway_account):
    with pytest.raises(
        ValueError, match="Arguments provider and client are mutually exclusive"
    ):
        Contract(address=1234, abi=[], client=gateway_client, provider=gateway_account)
