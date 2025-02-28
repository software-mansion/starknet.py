import datetime

import pytest

from starknet_py.constants import ANY_CALLER, OutsideExecutionInterfaceID
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import BaseAccount
from starknet_py.net.client_models import Call, OutsideExecutionTimeBounds
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.transaction_errors import TransactionRevertedError


@pytest.mark.asyncio
@pytest.mark.skip("TODO(#1560)")
async def test_argent_account_outside_execution_compatibility(
    argent_account: BaseAccount,
):
    result = await argent_account.supports_interface(OutsideExecutionInterfaceID.V1)
    assert result is True
    result = await argent_account.supports_interface(OutsideExecutionInterfaceID.V2)
    assert result is False


# TODO (#1546): Remove skip mark
@pytest.mark.skip
@pytest.mark.asyncio
async def test_account_outside_execution_any_caller(
    argent_account: BaseAccount,
    map_contract,
):

    assert any(
        [
            await argent_account.supports_interface(OutsideExecutionInterfaceID.V1),
            await argent_account.supports_interface(OutsideExecutionInterfaceID.V2),
        ]
    )

    put_call = Call(
        to_addr=map_contract.address,
        selector=get_selector_from_name("put"),
        calldata=[20, 20],
    )

    call = await argent_account.sign_outside_execution_call(
        calls=[
            put_call,
        ],
        execution_time_bounds=OutsideExecutionTimeBounds(
            execute_after=datetime.datetime.now() - datetime.timedelta(hours=1),
            execute_before=datetime.datetime.now() + datetime.timedelta(hours=1),
        ),
        caller=ANY_CALLER,
    )

    tx = await argent_account.execute_v3(
        calls=[call], resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await argent_account.client.wait_for_tx(tx.transaction_hash)


@pytest.mark.asyncio
@pytest.mark.skip("TODO(#1560)")
async def test_account_outside_execution_for_invalid_caller(
    argent_account: BaseAccount,
    account: BaseAccount,
    map_contract,
):
    assert any(
        [
            await argent_account.supports_interface(OutsideExecutionInterfaceID.V1),
            await argent_account.supports_interface(OutsideExecutionInterfaceID.V2),
        ]
    )

    put_call = Call(
        to_addr=map_contract.address,
        selector=get_selector_from_name("put"),
        calldata=[20, 20],
    )

    call = await argent_account.sign_outside_execution_call(
        calls=[
            put_call,
        ],
        execution_time_bounds=OutsideExecutionTimeBounds(
            execute_after=datetime.datetime.now() - datetime.timedelta(hours=1),
            execute_before=datetime.datetime.now() + datetime.timedelta(hours=1),
        ),
        caller=account.address,
    )

    tx = await argent_account.execute_v3(
        calls=[call], resource_bounds=MAX_RESOURCE_BOUNDS
    )

    with pytest.raises(TransactionRevertedError) as err:
        await argent_account.client.wait_for_tx(tx.transaction_hash)

    assert "argent/invalid-caller" in err.value.message


# TODO (#1546): Remove skip mark
@pytest.mark.skip
@pytest.mark.asyncio
async def test_account_outside_execution_for_impossible_time_bounds(
    argent_account: BaseAccount,
    map_contract,
):

    assert any(
        [
            await argent_account.supports_interface(OutsideExecutionInterfaceID.V1),
            await argent_account.supports_interface(OutsideExecutionInterfaceID.V2),
        ]
    )

    put_call = Call(
        to_addr=map_contract.address,
        selector=get_selector_from_name("put"),
        calldata=[20, 20],
    )

    call = await argent_account.sign_outside_execution_call(
        calls=[put_call],
        execution_time_bounds=OutsideExecutionTimeBounds(
            execute_after=datetime.datetime.now() - datetime.timedelta(days=10),
            execute_before=datetime.datetime.now() - datetime.timedelta(days=9),
        ),
        caller=ANY_CALLER,
    )

    tx = await argent_account.execute_v3(
        calls=[call], resource_bounds=MAX_RESOURCE_BOUNDS
    )

    with pytest.raises(TransactionRevertedError) as err:
        await argent_account.client.wait_for_tx(tx.transaction_hash)

    assert "argent/invalid-timestamp" in err.value.message
