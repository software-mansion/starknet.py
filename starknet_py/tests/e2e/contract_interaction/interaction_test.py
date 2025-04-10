import pytest

from starknet_py.contract import Contract, PreparedFunctionInvokeV3
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import Call, ResourceBounds, ResourceBoundsMapping
from starknet_py.net.models import InvokeV3
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_prepare_and_invoke_v3(map_contract):
    prepared_invoke = map_contract.functions["put"].prepare_invoke_v3(
        key=1, value=2, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    assert isinstance(prepared_invoke, PreparedFunctionInvokeV3)

    invocation = await prepared_invoke.invoke()
    assert isinstance(invocation.invoke_transaction, InvokeV3)
    assert invocation.invoke_transaction.resource_bounds == MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_invoke_v3(map_contract):
    invocation = await map_contract.functions["put"].invoke_v3(
        key=1, value=2, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    assert isinstance(invocation.invoke_transaction, InvokeV3)
    assert invocation.invoke_transaction.resource_bounds == MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_auto_fee_estimation_v3(map_contract):
    prepared_invoke = map_contract.functions["put"].prepare_invoke_v3(key=1, value=2)
    assert isinstance(prepared_invoke, PreparedFunctionInvokeV3)

    invocation = await prepared_invoke.invoke(auto_estimate=True)
    assert isinstance(invocation.invoke_transaction, InvokeV3)
    assert invocation.invoke_transaction.resource_bounds is not None


@pytest.mark.asyncio
async def test_throws_invoke_v3_without_resource_bounds(map_contract):
    error_message = (
        "One of arguments: "
        "resource_bounds or auto_estimate must be specified when invoking a transaction."
    )

    with pytest.raises(ValueError, match=error_message):
        await map_contract.functions["put"].invoke_v3(2, 3)


@pytest.mark.asyncio
async def test_throws_prepared_invoke_v3_without_resource_bounds(map_contract):
    error_message = (
        "One of arguments: "
        "resource_bounds or auto_estimate must be specified when invoking a transaction."
    )

    prepared_invoke = map_contract.functions["put"].prepare_invoke_v3(2, 3)
    assert isinstance(prepared_invoke, PreparedFunctionInvokeV3)

    with pytest.raises(ValueError, match=error_message):
        await prepared_invoke.invoke()


@pytest.mark.asyncio
async def test_throws_when_invoke_v3_with_resource_bounds_and_auto_estimate(
    map_contract,
):
    error_message = (
        "Arguments auto_estimate and resource_bounds are mutually exclusive."
    )

    prepared_invoke = map_contract.functions["put"].prepare_invoke_v3(key=2, value=3)
    with pytest.raises(ValueError, match=error_message):
        await prepared_invoke.invoke(
            resource_bounds=MAX_RESOURCE_BOUNDS, auto_estimate=True
        )


@pytest.mark.asyncio
async def test_latest_resource_bounds_takes_precedence(map_contract):
    prepared_function = map_contract.functions["put"].prepare_invoke_v3(
        key=1, value=2, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    invocation = await prepared_function.invoke(
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(
                max_amount=MAX_RESOURCE_BOUNDS.l1_gas.max_amount + 30,
                max_price_per_unit=MAX_RESOURCE_BOUNDS.l1_gas.max_price_per_unit + 30,
            ),
            l2_gas=ResourceBounds(
                max_amount=MAX_RESOURCE_BOUNDS.l2_gas.max_amount + 30,
                max_price_per_unit=MAX_RESOURCE_BOUNDS.l2_gas.max_price_per_unit + 30,
            ),
            l1_data_gas=ResourceBounds(
                max_amount=MAX_RESOURCE_BOUNDS.l1_data_gas.max_amount + 30,
                max_price_per_unit=MAX_RESOURCE_BOUNDS.l1_data_gas.max_price_per_unit
                + 30,
            ),
        )
    )

    assert isinstance(invocation.invoke_transaction, InvokeV3)

    for resource in ["l1_gas", "l2_gas", "l1_data_gas"]:
        for attr in ["max_amount", "max_price_per_unit"]:
            assert (
                getattr(
                    getattr(invocation.invoke_transaction.resource_bounds, resource),
                    attr,
                )
                == getattr(getattr(MAX_RESOURCE_BOUNDS, resource), attr) + 30
            )


@pytest.mark.asyncio
async def test_latest_resource_bounds_take_precedence(map_contract):
    prepared_function = map_contract.functions["put"].prepare_invoke_v3(
        key=1, value=2, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    updated_resource_bounds = ResourceBoundsMapping(
        l1_gas=ResourceBounds(
            max_amount=MAX_RESOURCE_BOUNDS.l1_gas.max_amount + 100,
            max_price_per_unit=MAX_RESOURCE_BOUNDS.l1_gas.max_price_per_unit + 200,
        ),
        l2_gas=ResourceBounds(
            max_amount=MAX_RESOURCE_BOUNDS.l2_gas.max_amount + 100,
            max_price_per_unit=MAX_RESOURCE_BOUNDS.l2_gas.max_price_per_unit + 200,
        ),
        l1_data_gas=ResourceBounds(
            max_amount=MAX_RESOURCE_BOUNDS.l1_data_gas.max_amount + 100,
            max_price_per_unit=MAX_RESOURCE_BOUNDS.l1_data_gas.max_price_per_unit + 200,
        ),
    )
    invocation = await prepared_function.invoke(resource_bounds=updated_resource_bounds)

    assert isinstance(invocation.invoke_transaction, InvokeV3)
    assert (
        invocation.invoke_transaction.resource_bounds.l1_gas
        == updated_resource_bounds.l1_gas
    )
    assert (
        invocation.invoke_transaction.resource_bounds.l2_gas
        == updated_resource_bounds.l2_gas
    )
    assert (
        invocation.invoke_transaction.resource_bounds.l1_data_gas
        == updated_resource_bounds.l1_data_gas
    )


@pytest.mark.asyncio
async def test_prepare_without_resource_bounds(map_contract):
    prepared_invoke = map_contract.functions["put"].prepare_invoke_v3(key=1, value=2)

    assert prepared_invoke.resource_bounds is None


@pytest.mark.asyncio
@pytest.mark.parametrize("key, value", ((2, 13), (412312, 32134), (12345, 3567)))
async def test_invoke_v3_and_call(key, value, map_contract):
    invocation = await map_contract.functions["put"].invoke_v3(
        key, value, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await invocation.wait_for_acceptance()
    assert isinstance(invocation.invoke_transaction, InvokeV3)

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
    transaction = await map_contract.functions["put"].invoke_v3(
        key=10, value=20, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await client.wait_for_tx(transaction.hash)


@pytest.mark.asyncio
async def test_error_when_prepare_without_account(client, map_contract):
    contract = await Contract.from_address(map_contract.address, client)

    with pytest.raises(
        ValueError,
        match="Contract instance was created without providing an Account.",
    ):
        contract.functions["put"].prepare_invoke_v3(key=10, value=10)


@pytest.mark.asyncio
async def test_error_when_invoke_without_account(client, map_contract):
    contract = await Contract.from_address(map_contract.address, client)

    with pytest.raises(
        ValueError,
        match="Contract instance was created without providing an Account.",
    ):
        await contract.functions["put"].invoke_v3(key=10, value=10)
