import asyncio
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starkware_utils.error_handling import StarkErrorCode

from starknet_py.net.client_models import SentTransactionResponse
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.transaction_exceptions import TransactionRejectedError
from starknet_py.contract import Contract
from starknet_py.net.models import InvokeFunction
from starknet_py.tests.e2e.utils import DevnetClientFactory
from starknet_py.net.client_errors import ClientError, ContractNotFoundError

directory = os.path.dirname(__file__)

map_source = Path(directory, "map.cairo").read_text("utf-8")
proxy_source = Path(directory, "argent_proxy.cairo").read_text("utf-8")

MAX_FEE = int(1e20)


@pytest.mark.asyncio
async def test_max_fee_is_set_in_sent_invoke(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    prepared_call = contract.functions["put"].prepare(key, value, max_fee=100)
    assert prepared_call.max_fee == 100
    invocation = await prepared_call.invoke()
    assert invocation.invoke_transaction.max_fee == 100

    invocation = await contract.functions["put"].invoke(key, value, max_fee=200)
    assert invocation.invoke_transaction.max_fee == 200

    prepared_call = contract.functions["put"].prepare(key, value, max_fee=300)
    assert prepared_call.max_fee == 300
    invocation = await prepared_call.invoke(max_fee=400)
    assert invocation.invoke_transaction.max_fee == 400


@pytest.mark.asyncio
async def test_auto_fee_estimation(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    prepared_call = contract.functions["put"].prepare(key, value)
    invocation = await prepared_call.invoke(auto_estimate=True)

    assert invocation.invoke_transaction.max_fee is not None


@pytest.mark.asyncio
async def test_throws_on_estimate_with_positive_max_fee(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    prepared_call = contract.functions["put"].prepare(key, value, max_fee=100)
    with pytest.raises(ValueError) as exinfo:
        await prepared_call.estimate_fee()

    assert (
        "Cannot estimate fee of PreparedFunctionCall with max_fee not None or 0."
        in str(exinfo.value)
    )


@pytest.mark.asyncio
async def test_throws_on_both_max_fee_and_auto_estimate(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    invocation = contract.functions["put"].prepare(key, value)
    with pytest.raises(ValueError) as exinfo:
        await invocation.invoke(max_fee=10, auto_estimate=True)

    assert (
        "Max_fee and auto_estimate are exclusive and cannot be provided at the same time."
        in str(exinfo.value)
    )


@pytest.mark.asyncio
async def test_throws_on_both_max_fee_in_prepare_and_auto_estimate(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    invocation = contract.functions["put"].prepare(key, value, max_fee=2000)
    with pytest.raises(ValueError) as exinfo:
        await invocation.invoke(auto_estimate=True)

    assert (
        "Max_fee and auto_estimate are exclusive and cannot be provided at the same time."
        in str(exinfo.value)
    )


@pytest.mark.asyncio
async def test_throws_on_call_without_max_fee(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    with pytest.raises(ValueError) as exinfo:
        await contract.functions["put"].invoke(key, value)

    assert "Max_fee must be specified when invoking a transaction" in str(exinfo.value)


@pytest.mark.asyncio
async def test_throws_on_prepared_call_without_max_fee(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    prepared_call = contract.functions["put"].prepare(key, value)

    with pytest.raises(ValueError) as exinfo:
        await prepared_call.invoke()

    assert "Max_fee must be specified when invoking a transaction" in str(exinfo.value)


@pytest.mark.asyncio
async def test_latest_max_fee_takes_precedence(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    prepared_function = contract.functions["put"].prepare(key, value, max_fee=20)
    invocation = await prepared_function.invoke(max_fee=50)

    assert invocation.invoke_transaction.max_fee == 50


@pytest.mark.asyncio
async def test_prepare_without_max_fee(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    prepared_call = contract.functions["put"].prepare(key, value)

    assert prepared_call.max_fee is None


@pytest.mark.asyncio
@pytest.mark.parametrize("key, value", ((2, 13), (412312, 32134), (12345, 3567)))
async def test_invoke_and_call(key, value, run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()

    # Deploy simple k-v store
    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    invocation = await contract.functions["put"].invoke(key, value, max_fee=MAX_FEE)
    await invocation.wait_for_acceptance()
    (response,) = await contract.functions["get"].call(key)

    assert response == value


user_auth_source = Path(directory, "user_auth.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_get_code_not_found(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()

    with pytest.raises(ContractNotFoundError) as exinfo:
        await Contract.from_address(1, client)

    assert "No contract found" in str(exinfo.value)


@pytest.mark.asyncio
async def test_call_unitinialized_contract(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()

    with pytest.raises(ClientError) as exinfo:
        await client.call_contract(
            InvokeFunction(
                contract_address=1,
                entry_point_selector=get_selector_from_name("get_nonce"),
                calldata=[],
                signature=[],
                max_fee=MAX_FEE,
                version=0,
            )
        )

    assert "500" in str(exinfo.value)


@pytest.mark.asyncio
async def test_deploy_throws_on_no_compilation_source(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()

    with pytest.raises(ValueError) as exinfo:
        await Contract.deploy(client=client)

    assert "One of compiled_contract or compilation_source is required." in str(
        exinfo.value
    )


@pytest.mark.asyncio
async def test_wait_for_tx_devnet(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()

    deployment = await Contract.deploy(compilation_source=map_source, client=client)
    await client.wait_for_tx(deployment.hash)


@pytest.mark.run_on_testnet
@pytest.mark.asyncio
async def test_wait_for_tx_testnet():
    client = GatewayClient(net="testnet")

    deployment = await Contract.deploy(compilation_source=map_source, client=client)
    await client.wait_for_tx(deployment.hash)


@pytest.mark.asyncio
async def test_wait_for_tx_throws_on_transaction_rejected(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()
    deploy = await Contract.deploy(compilation_source=map_source, client=client)
    contract = deploy.deployed_contract
    invoke = contract.functions["put"].prepare(key=0x1, value=0x1, max_fee=MAX_FEE)

    # modify selector so that transaction will get rejected
    invoke.selector = 0x0123
    transaction = await invoke.invoke()

    with pytest.raises(TransactionRejectedError):
        await client.wait_for_tx(transaction.hash)


@pytest.mark.asyncio
async def test_contract_from_address_with_1_proxy(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client_without_account()
    map_contract = await Contract.deploy(compilation_source=map_source, client=client)
    deployment_result = await Contract.deploy(
        compilation_source=proxy_source,
        constructor_args=[map_contract.deployed_contract.address],
        client=client,
    )

    proxy_contract = await Contract.from_address(
        deployment_result.deployed_contract.address,
        client=client,
        proxy_config=True,
    )

    assert all(f in proxy_contract.functions for f in ("put", "get"))


@pytest.mark.asyncio
async def test_contract_from_address_with_2_proxy(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client_without_account()
    map_contract = await Contract.deploy(compilation_source=map_source, client=client)
    proxy1_deployment = await Contract.deploy(
        compilation_source=proxy_source,
        constructor_args=[map_contract.deployed_contract.address],
        client=client,
    )
    proxy2_deployment = await Contract.deploy(
        compilation_source=proxy_source,
        constructor_args=[proxy1_deployment.deployed_contract.address],
        client=client,
    )

    proxy_contract = await Contract.from_address(
        proxy2_deployment.deployed_contract.address,
        client=client,
        proxy_config=True,
    )

    assert all(f in proxy_contract.functions for f in ("put", "get"))


@pytest.mark.asyncio
async def test_contract_from_address_throws_on_too_many_steps(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client_without_account()
    map_contract = await Contract.deploy(compilation_source=map_source, client=client)
    proxy1_deployment = await Contract.deploy(
        compilation_source=proxy_source,
        constructor_args=[map_contract.deployed_contract.address],
        client=client,
    )
    proxy2_deployment = await Contract.deploy(
        compilation_source=proxy_source,
        constructor_args=[proxy1_deployment.deployed_contract.address],
        client=client,
    )

    with pytest.raises(RecursionError) as exinfo:
        await Contract.from_address(
            proxy2_deployment.deployed_contract.address,
            client=client,
            proxy_config={"max_steps": 2},
        )

    assert "Max number of steps exceeded" in str(exinfo.value)


@pytest.mark.asyncio
async def test_contract_from_address_throws_on_proxy_cycle(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()
    proxy1_deployment = await Contract.deploy(
        compilation_source=proxy_source,
        constructor_args=[0x123],
        client=client,
    )
    proxy2_deployment = await Contract.deploy(
        compilation_source=proxy_source,
        constructor_args=[0x123],
        client=client,
    )
    await proxy1_deployment.wait_for_acceptance()
    await proxy2_deployment.wait_for_acceptance()

    proxy1 = proxy1_deployment.deployed_contract
    proxy2 = proxy2_deployment.deployed_contract

    await proxy1.functions["_set_implementation"].invoke(
        implementation=proxy2.address, max_fee=MAX_FEE
    )
    await proxy2.functions["_set_implementation"].invoke(
        implementation=proxy1.address, max_fee=MAX_FEE
    )

    with pytest.raises(RecursionError) as exinfo:
        await Contract.from_address(
            address=proxy2_deployment.deployed_contract.address,
            client=client,
            proxy_config=True,
        )

    assert "Proxy cycle detected" in str(exinfo.value)


@pytest.mark.asyncio
async def test_warning_when_max_fee_equals_to_zero(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()

    # Deploy simple k-v store
    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    with pytest.warns(
        DeprecationWarning,
        match=r"Transaction will fail with max_fee set to 0. Change it to a higher value.",
    ) as max_fee_warnings:
        await contract.functions["put"].invoke(10, 20, max_fee=0)

    assert len(max_fee_warnings) == 1


@pytest.mark.asyncio
async def test_transaction_not_received_error(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client()

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    with patch(
        "starknet_py.net.account.account_client.AccountClient.send_transaction",
        MagicMock(),
    ) as mocked_send_transaction:
        result = asyncio.Future()
        result.set_result(
            SentTransactionResponse(
                code=StarkErrorCode.TRANSACTION_CANCELLED.value, hash=0x123
            )
        )

        mocked_send_transaction.return_value = result

        with pytest.raises(Exception) as tx_not_received:
            await contract.functions["put"].invoke(10, 20, max_fee=MAX_FEE)

        assert "Failed to send transaction." in str(tx_not_received)


@pytest.mark.asyncio
async def test_error_when_invoking_without_account_client(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client_without_account()

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    with pytest.raises(ValueError) as wrong_client_error:
        await contract.functions["put"].prepare(key=10, value=10).invoke(
            max_fee=MAX_FEE
        )

    assert (
        "Contract uses an account that can't invoke transactions. You need to use AccountClient for that."
        in str(wrong_client_error)
    )


@pytest.mark.asyncio
async def test_error_when_estimating_fee_while_not_using_account_client(run_devnet):
    client = DevnetClientFactory(run_devnet).make_devnet_client_without_account()

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    with pytest.raises(ValueError) as wrong_client_error:
        await contract.functions["put"].prepare(key=10, value=10).estimate_fee()

    assert (
        "Contract uses an account that can't invoke transactions. You need to use AccountClient for that."
        in str(wrong_client_error)
    )
