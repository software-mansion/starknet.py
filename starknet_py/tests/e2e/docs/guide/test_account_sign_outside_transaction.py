import pytest

from starknet_py.net.client_models import TransactionFinalityStatus


@pytest.mark.asyncio
async def test_account_outside_execution_any_caller(
    account,
    argent_account,
    map_contract,
):
    # pylint: disable=import-outside-toplevel,too-many-locals

    # docs: start
    import datetime

    from starknet_py.constants import ANY_CALLER
    from starknet_py.hash.selector import get_selector_from_name
    from starknet_py.net.client_models import Call, OutsideExecutionTimeBounds

    # Create a call to put value 20 under key 20. That will be executed
    # as part of outside execution.

    put_call = Call(
        to_addr=map_contract.address,
        selector=get_selector_from_name("put"),
        calldata=[20, 20],
    )

    # Create a special signed execution call. This call can now be executed by
    # the caller specified. In this case, caller is ANY_CALLER, a special constant
    # that allows any caller to execute the call.
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

    # Execute the call as a normal invoke transaction
    # can be executed from any account specified in the caller field
    tx = await account.execute_v1(calls=[call], max_fee=int(1e18))
    await account.client.wait_for_tx(tx.transaction_hash)

    # docs: end

    receipt = await account.client.get_transaction_receipt(tx_hash=tx.transaction_hash)

    assert receipt.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2
