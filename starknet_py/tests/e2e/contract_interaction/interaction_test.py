import pytest

from starknet_py.contract import Contract
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import Call, ResourceBounds, ResourceBoundsMapping
from starknet_py.net.models import InvokeV1, InvokeV3
from starknet_py.tests.e2e.fixtures.constants import (
    MAX_FEE,
    MAX_RESOURCE_BOUNDS,
    MAX_RESOURCE_BOUNDS_L1,
)

key, value = 1, 2


@pytest.mark.asyncio
async def test_prepare_and_invoke_v1(map_contract):
    prepared_call = map_contract.functions["put"].prepare(
        key, value, tx_version=1, max_fee=MAX_FEE
    )
    assert prepared_call.l1_resource_bounds is None
    assert prepared_call.max_fee == MAX_FEE
    assert prepared_call.tx_version == 1

    invocation = await prepared_call.invoke()
    assert isinstance(invocation.invoke_transaction, InvokeV1)
    assert invocation.invoke_transaction.max_fee == MAX_FEE


@pytest.mark.asyncio
async def test_prepare_and_invoke_v3(map_contract):
    prepared_call = map_contract.functions["put"].prepare(
        key, value, tx_version=3, l1_resource_bounds=MAX_RESOURCE_BOUNDS_L1
    )
    assert prepared_call.max_fee is None
    assert prepared_call.l1_resource_bounds == MAX_RESOURCE_BOUNDS_L1
    assert prepared_call.tx_version == 3

    invocation = await prepared_call.invoke()
    assert isinstance(invocation.invoke_transaction, InvokeV3)
    assert invocation.invoke_transaction.resource_bounds == MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_invoke_v1(map_contract):
    invocation = await map_contract.functions["put"].invoke(
        key, value, tx_version=1, max_fee=MAX_FEE
    )
    assert isinstance(invocation.invoke_transaction, InvokeV1)
    assert invocation.invoke_transaction.max_fee == MAX_FEE


@pytest.mark.asyncio
async def test_invoke_v3(map_contract):
    invocation = await map_contract.functions["put"].invoke(
        key, value, tx_version=3, l1_resource_bounds=MAX_RESOURCE_BOUNDS_L1
    )
    assert isinstance(invocation.invoke_transaction, InvokeV3)
    assert invocation.invoke_transaction.resource_bounds == MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_auto_fee_estimation_v1(map_contract):
    prepared_call = map_contract.functions["put"].prepare(key, value, tx_version=1)
    assert prepared_call.tx_version == 1

    invocation = await prepared_call.invoke(auto_estimate=True)

    assert isinstance(invocation.invoke_transaction, InvokeV1)
    assert invocation.invoke_transaction.max_fee is not None


@pytest.mark.asyncio
async def test_auto_fee_estimation_v3(map_contract):
    prepared_call = map_contract.functions["put"].prepare(key, value, tx_version=3)
    assert prepared_call.tx_version == 3

    invocation = await prepared_call.invoke(auto_estimate=True)

    assert isinstance(invocation.invoke_transaction, InvokeV3)
    assert invocation.invoke_transaction.resource_bounds is not None


@pytest.mark.asyncio
async def test_throws_invoke_v1_without_max_fee(map_contract):
    error_message = "Argument max_fee must be specified when invoking a transaction."

    with pytest.raises(ValueError, match=error_message):
        await map_contract.functions["put"].invoke(key, value, tx_version=1)


@pytest.mark.asyncio
async def test_throws_invoke_v3_without_resource_bounds(map_contract):
    error_message = (
        "One of arguments: "
        "l1_resource_bounds or auto_estimate must be specified when invoking a transaction."
    )

    with pytest.raises(ValueError, match=error_message):
        await map_contract.functions["put"].invoke(key, value, tx_version=3)


@pytest.mark.asyncio
async def test_throws_prepared_call_invoke_v1_without_max_fee(map_contract):
    error_message = "Argument max_fee must be specified when invoking a transaction."

    prepared_call = map_contract.functions["put"].prepare(key, value, tx_version=1)
    with pytest.raises(ValueError, match=error_message):
        await prepared_call.invoke()


@pytest.mark.asyncio
async def test_throws_prepared_call_invoke_v3_without_resource_bounds(map_contract):
    error_message = (
        "One of arguments: "
        "l1_resource_bounds or auto_estimate must be specified when invoking a transaction."
    )

    prepared_call = map_contract.functions["put"].prepare(key, value, tx_version=3)
    with pytest.raises(ValueError, match=error_message):
        await prepared_call.invoke()


@pytest.mark.asyncio
async def test_throws_prepared_call_with_max_fee_invoke_v1_with_auto_estimate(
    map_contract,
):
    error_message = "Arguments max_fee and auto_estimate are mutually exclusive."

    invocation = map_contract.functions["put"].prepare(
        key, value, tx_version=1, max_fee=2000
    )
    with pytest.raises(ValueError, match=error_message):
        await invocation.invoke(auto_estimate=True)


@pytest.mark.asyncio
async def test_throws_prepared_call_with_resource_bounds_invoke_v3_with_auto_estimate(
    map_contract,
):
    error_message = (
        "Arguments l1_resource_bounds and auto_estimate are mutually exclusive."
    )

    invocation = map_contract.functions["put"].prepare(
        key, value, l1_resource_bounds=MAX_RESOURCE_BOUNDS_L1, tx_version=3
    )
    with pytest.raises(ValueError, match=error_message):
        await invocation.invoke(auto_estimate=True)


@pytest.mark.asyncio
async def test_throws_invoke_v1_with_max_fee_and_auto_estimate(map_contract):
    error_message = "Arguments max_fee and auto_estimate are mutually exclusive."

    prepared_call = map_contract.functions["put"].prepare(key, value, tx_version=1)
    with pytest.raises(ValueError, match=error_message):
        await prepared_call.invoke(max_fee=10, auto_estimate=True)


@pytest.mark.asyncio
async def test_throws_invoke_v3_with_resource_bounds_and_auto_estimate(map_contract):
    error_message = (
        "Arguments l1_resource_bounds and auto_estimate are mutually exclusive."
    )

    with pytest.raises(ValueError, match=error_message):
        await map_contract.functions["put"].invoke(
            key,
            value,
            tx_version=3,
            l1_resource_bounds=MAX_RESOURCE_BOUNDS_L1,
            auto_estimate=True,
        )


@pytest.mark.asyncio
async def test_throws_invalid_invoke_version(map_contract):
    error_message = "The allowed versions for Invoke transaction are 1 or 3."

    prepared_call = map_contract.functions["put"].prepare(key, value, tx_version=2)
    with pytest.raises(ValueError, match=error_message):
        await prepared_call.invoke(auto_estimate=True)


@pytest.mark.asyncio
async def test_throws_when_max_fee_and_resource_bounds(map_contract):
    error_message = (
        "Arguments 'max_fee' and 'l1_resource_bounds' are mutually exclusive."
    )

    prepared_call = map_contract.functions["put"].prepare(key, value)
    with pytest.raises(ValueError, match=error_message):
        await prepared_call.invoke(
            max_fee=MAX_FEE, l1_resource_bounds=MAX_RESOURCE_BOUNDS_L1
        )


@pytest.mark.asyncio
async def test_throws_no_tx_version(map_contract):
    error_message = (
        "The transaction version is not specified. "
        "Please ensure that the 'tx_version' is set to either 1 or 3."
    )

    prepared_call = map_contract.functions["put"].prepare(key, value)
    with pytest.raises(ValueError, match=error_message):
        await prepared_call.invoke(max_fee=MAX_FEE)


@pytest.mark.asyncio
async def test_latest_max_fee_takes_precedence(map_contract):
    prepared_function = map_contract.functions["put"].prepare(
        key, value, tx_version=1, max_fee=MAX_FEE
    )
    invocation = await prepared_function.invoke(max_fee=MAX_FEE + 30)

    assert isinstance(invocation.invoke_transaction, InvokeV1)
    assert invocation.invoke_transaction.max_fee == MAX_FEE + 30


@pytest.mark.asyncio
async def test_latest_resource_bounds_take_precedence(map_contract):
    prepared_function = map_contract.functions["put"].prepare(
        key, value, l1_resource_bounds=MAX_RESOURCE_BOUNDS_L1, tx_version=3
    )

    updated_resource_bounds = ResourceBounds(
        max_amount=MAX_RESOURCE_BOUNDS_L1.max_amount + 100,
        max_price_per_unit=MAX_RESOURCE_BOUNDS_L1.max_price_per_unit + 10,
    )
    invocation = await prepared_function.invoke(
        l1_resource_bounds=updated_resource_bounds
    )

    assert isinstance(invocation.invoke_transaction, InvokeV3)
    assert invocation.invoke_transaction.resource_bounds == ResourceBoundsMapping(
        l1_gas=updated_resource_bounds, l2_gas=ResourceBounds.init_with_zeros()
    )


@pytest.mark.asyncio
async def test_prepare_without_max_fee(map_contract):
    prepared_call = map_contract.functions["put"].prepare(key, value, tx_version=1)

    assert prepared_call.max_fee is None


@pytest.mark.asyncio
@pytest.mark.parametrize("k, v", ((2, 13), (412312, 32134), (12345, 3567)))
async def test_invoke_and_call(k, v, map_contract):
    invocation = await map_contract.functions["put"].invoke(
        k, v, tx_version=1, max_fee=MAX_FEE
    )
    await invocation.wait_for_acceptance()

    assert isinstance(invocation.invoke_transaction, InvokeV1)
    (response,) = await map_contract.functions["get"].call(k)

    assert response == v


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
        key=10, value=20, tx_version=1, max_fee=MAX_FEE
    )
    await client.wait_for_tx(transaction.hash)


@pytest.mark.asyncio
async def test_error_when_invoking_without_account(client, map_contract):
    contract = await Contract.from_address(map_contract.address, client)

    with pytest.raises(
        ValueError,
        match="Contract instance was created without providing an Account.",
    ):
        await contract.functions["put"].prepare(key=10, value=10, tx_version=1).invoke(
            max_fee=MAX_FEE
        )


@pytest.mark.asyncio
async def test_error_when_estimating_fee_while_not_using_account(client, map_contract):
    contract = await Contract.from_address(map_contract.address, client)

    with pytest.raises(
        ValueError,
        match="Contract instance was created without providing an Account.",
    ):
        await contract.functions["put"].prepare(
            key=10, value=10, tx_version=1
        ).estimate_fee()
