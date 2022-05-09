import os
from pathlib import Path

import pytest
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.contract import Contract
from starknet_py.net.client import BadRequest
from starknet_py.net.models import InvokeFunction
from starknet_py.tests.e2e.utils import DevnetClientFactory
from starknet_py.utils.crypto.facade import sign_calldata

directory = os.path.dirname(__file__)

map_source = Path(directory, "map.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_max_fee_is_set_in_sent_invoke(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)

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
    client = await DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)

    prepared_call = contract.functions["put"].prepare(key, value)
    invocation = await prepared_call.invoke(auto_estimate=True)

    assert invocation.invoke_transaction.max_fee is not None


@pytest.mark.asyncio
async def test_throws_on_estimate_with_positive_max_fee(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)

    prepared_call = contract.functions["put"].prepare(key, value, max_fee=100)
    with pytest.raises(ValueError) as exinfo:
        await prepared_call.estimate_fee()

    assert (
        "Cannot estimate fee of PreparedFunctionCall with max_fee not None or 0."
        in str(exinfo.value)
    )


@pytest.mark.asyncio
async def test_throws_on_both_max_fee_and_auto_estimate(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)

    invocation = contract.functions["put"].prepare(key, value)
    with pytest.raises(ValueError) as exinfo:
        await invocation.invoke(max_fee=10, auto_estimate=True)

    assert (
        "Max_fee and auto_estimate are exclusive and cannot be provided at the same time."
        in str(exinfo.value)
    )


@pytest.mark.asyncio
async def test_throws_on_both_max_fee_in_prepare_and_auto_estimate(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)

    invocation = contract.functions["put"].prepare(key, value, max_fee=2000)
    with pytest.raises(ValueError) as exinfo:
        await invocation.invoke(auto_estimate=True)

    assert (
        "Auto_estimate cannot be used if max_fee was provided when preparing a function call."
        in str(exinfo.value)
    )


@pytest.mark.asyncio
async def test_throws_on_call_without_max_fee(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)

    with pytest.raises(ValueError) as exinfo:
        await contract.functions["put"].invoke(key, value)

    assert "Max_fee must be specified when invoking a transaction" in str(exinfo.value)


@pytest.mark.asyncio
async def test_throws_on_prepared_call_without_max_fee(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)
    prepared_call = contract.functions["put"].prepare(key, value)

    with pytest.raises(ValueError) as exinfo:
        await prepared_call.invoke()

    assert "Max_fee must be specified when invoking a transaction" in str(exinfo.value)


@pytest.mark.asyncio
async def test_latest_max_fee_takes_precedence(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)

    prepared_function = contract.functions["put"].prepare(key, value, max_fee=20)
    invocation = await prepared_function.invoke(max_fee=50)

    assert invocation.invoke_transaction.max_fee == 50


@pytest.mark.asyncio
async def test_prepare_without_max_fee(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)
    prepared_call = contract.functions["put"].prepare(key, value)

    assert prepared_call.max_fee is None


@pytest.mark.asyncio
@pytest.mark.parametrize("key, value", ((2, 13), (412312, 32134), (12345, 3567)))
async def test_invoke_and_call(key, value, run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()

    # Deploy simple k-v store
    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)
    invocation = await contract.functions["put"].invoke(key, value, max_fee=0)
    await invocation.wait_for_acceptance()
    (response,) = await contract.functions["get"].call(key)

    assert response == value


user_auth_source = Path(directory, "user_auth.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_signature(run_devnet):
    """
    Based on https://www.cairo-lang.org/docs/hello_starknet/user_auth.html#interacting-with-the-contract
    but replaced with struct
    """
    client = await DevnetClientFactory(run_devnet).make_devnet_client_without_account()
    private_key = 12345
    public_key = (
        1628448741648245036800002906075225705100596136133912895015035902954123957052
    )
    details = {"favourite_number": 1, "favourite_tuple": (2, 3, 4)}

    deployment_result = await Contract.deploy(
        client=client, compilation_source=user_auth_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    contract = await Contract.from_address(contract.address, client)

    fun_call = contract.functions["set_details"].prepare(
        public_key, details, max_fee=0, version=0
    )

    # Verify that it doesn't work with proper signature
    with pytest.raises(Exception):
        invocation = await fun_call.invoke(signature=[1, 2])
        await invocation.wait_for_acceptance()

    signature = sign_calldata(fun_call.arguments["details"], private_key)
    invocation = await fun_call.invoke(signature=signature)
    await invocation.wait_for_acceptance()

    (balance,) = await contract.functions["get_details"].call(public_key)

    assert balance == details


@pytest.mark.asyncio
async def test_get_code_not_found(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()

    with pytest.raises(BadRequest) as exinfo:
        await Contract.from_address(1, client)

    assert "not found" in str(exinfo.value)


@pytest.mark.asyncio
async def test_call_unitinialized_contract(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()

    with pytest.raises(BadRequest) as exinfo:
        await client.call_contract(
            InvokeFunction(
                contract_address=1,
                entry_point_selector=get_selector_from_name("get_nonce"),
                calldata=[],
                signature=[],
                max_fee=50000,
                version=0,
            )
        )

    assert "500" in str(exinfo.value)


@pytest.mark.asyncio
async def test_deploy_throws_on_no_compilation_source(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()

    with pytest.raises(ValueError) as exinfo:
        await Contract.deploy(client=client)

    assert "One of compiled_contract or compilation_source is required." in str(
        exinfo.value
    )
