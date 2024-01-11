import pytest

from starknet_py.common import create_compiled_contract
from starknet_py.contract import Contract
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import Call
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


@pytest.mark.asyncio
async def test_max_fee_is_set_in_sent_invoke(map_contract):
    key = 2
    value = 3

    prepared_call = map_contract.functions["put"].prepare(key, value, max_fee=MAX_FEE)
    assert prepared_call.max_fee == MAX_FEE

    invocation = await prepared_call.invoke()
    assert invocation.invoke_transaction.max_fee == MAX_FEE

    invocation = await map_contract.functions["put"].invoke(
        key, value, max_fee=MAX_FEE + 100
    )
    assert invocation.invoke_transaction.max_fee == MAX_FEE + 100

    prepared_call = map_contract.functions["put"].prepare(
        key, value, max_fee=MAX_FEE + 200
    )
    assert prepared_call.max_fee == MAX_FEE + 200

    invocation = await prepared_call.invoke(max_fee=MAX_FEE + 300)
    assert invocation.invoke_transaction.max_fee == MAX_FEE + 300


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

    prepared_function = map_contract.functions["put"].prepare(
        key, value, max_fee=MAX_FEE
    )
    invocation = await prepared_function.invoke(max_fee=MAX_FEE + 30)

    assert invocation.invoke_transaction.max_fee == MAX_FEE + 30


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
    await invocation.wait_for_acceptance()
    (response,) = await map_contract.functions["get"].call(key)

    assert response == value


@pytest.mark.asyncio
async def test_call_uninitialized_contract(client):
    with pytest.raises(ClientError, match="Contract not found"):
        await client.call_contract(
            Call(
                to_addr=1,
                selector=get_selector_from_name("get_nonce"),
                calldata=[],
            ),
            block_hash="latest",
        )


@pytest.mark.asyncio
async def test_wait_for_tx(client, map_contract):
    transaction = await map_contract.functions["put"].invoke(
        key=10, value=20, max_fee=MAX_FEE
    )
    await client.wait_for_tx(transaction.hash)


@pytest.mark.asyncio
async def test_error_when_invoking_without_account(client, map_contract):
    contract = await Contract.from_address(map_contract.address, client)

    with pytest.raises(
        ValueError,
        match="Contract instance was created without providing an Account.",
    ):
        await contract.functions["put"].prepare(key=10, value=10).invoke(
            max_fee=MAX_FEE
        )


@pytest.mark.asyncio
async def test_error_when_estimating_fee_while_not_using_account(client, map_contract):
    contract = await Contract.from_address(map_contract.address, client)

    with pytest.raises(
        ValueError,
        match="Contract instance was created without providing an Account.",
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
