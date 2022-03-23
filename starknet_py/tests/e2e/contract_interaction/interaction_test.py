import os
from pathlib import Path

import pytest
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.contract import Contract
from starknet_py.net.client import BadRequest
from starknet_py.net.models import InvokeFunction
from starknet_py.tests.e2e.utils import DevnetClient, DevnetClientNoAccount
from starknet_py.utils.crypto.facade import sign_calldata

directory = os.path.dirname(__file__)

map_source = Path(directory, "map.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_auto_fee_estimation():
    client = await DevnetClient.make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)
    invocation = await contract.functions["put"].invoke(key, value, auto_estimate=True)
    await invocation.wait_for_acceptance()
    (response,) = await contract.functions["get"].call(key)

    assert response == value


@pytest.mark.asyncio
async def test_max_fee_takes_precedence_over_auto_setimate():
    client = await DevnetClient.make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)

    invocation = contract.functions["put"].prepare(
        key, value, max_fee=0, auto_estimate=True
    )
    assert invocation.max_fee == 0


@pytest.mark.asyncio
async def test_prepare_without_max_fee():
    client = await DevnetClient.make_devnet_client()
    key = 2
    value = 3

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract = await Contract.from_address(contract.address, client)
    prepared_call = contract.functions["put"].prepare(key, value)

    assert prepared_call.max_fee == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("key, value", ((2, 13), (412312, 32134), (12345, 3567)))
async def test_invoke_and_call(key, value):
    client = await DevnetClient.make_devnet_client()

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
async def test_signature():
    """
    Based on https://www.cairo-lang.org/docs/hello_starknet/user_auth.html#interacting-with-the-contract
    but replaced with struct
    """
    client = DevnetClientNoAccount()
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
async def test_get_code_not_found():
    client = await DevnetClient.make_devnet_client()

    with pytest.raises(BadRequest) as exinfo:
        await Contract.from_address(1, client)

    assert "not found" in str(exinfo.value)


@pytest.mark.asyncio
async def test_call_unitinialized_contract():
    client = await DevnetClient.make_devnet_client()

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
