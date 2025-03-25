import pytest

from starknet_py.net.client_models import (
    ResourceBoundsMapping,
    TransactionFinalityStatus,
)


@pytest.mark.asyncio
async def test_account_outside_execution_any_caller(
    account,
    argent_account_v040,
    map_contract,
):
    # pylint: disable=import-outside-toplevel,too-many-locals

    # docs: start
    import datetime

    from starknet_py.constants import ANY_CALLER
    from starknet_py.hash.selector import get_selector_from_name
    from starknet_py.net.client_models import (
        Call,
        OutsideExecutionTimeBounds,
        ResourceBounds,
    )

    # Create a call to put value 100 at key 1.
    put_call = Call(
        to_addr=map_contract.address,
        selector=get_selector_from_name("put"),
        calldata=[1, 100],
    )

    # Create an outside execution call. This call can now be executed by
    # the specified caller. In this case, anyone will be able to execute it.

    # Note that signing account does not need to have any funds to sign the transaction.
    call = await argent_account_v040.sign_outside_execution_call(
        calls=[
            put_call,
        ],
        # The transaction can be executed in specified timeframe.
        execution_time_bounds=OutsideExecutionTimeBounds(
            execute_after=datetime.datetime.now() - datetime.timedelta(hours=1),
            execute_before=datetime.datetime.now() + datetime.timedelta(hours=1),
        ),
        # Use ANY_CALLER, a special constant that allows anyone to execute the call.
        caller=ANY_CALLER,
    )

    # Now, if you're in specified timeframe, you can perform the outside execution by another account.
    tx = await account.execute_v3(
        calls=[call],
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17)),
            l1_data_gas=ResourceBounds(
                max_amount=int(1e5), max_price_per_unit=int(1e13)
            ),
        ),
    )
    await account.client.wait_for_tx(tx.transaction_hash)

    # docs: end

    receipt = await account.client.get_transaction_receipt(tx_hash=tx.transaction_hash)

    assert receipt.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2
