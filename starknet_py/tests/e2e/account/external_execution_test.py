import datetime

import pytest

from starknet_py.constants import ANY_CALLER, SNIP9InterfaceVersion
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account, BaseAccount
from starknet_py.net.client_models import Call, ExecutionTimeBounds
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE
from starknet_py.transaction_errors import TransactionRevertedError


@pytest.mark.asyncio
async def test_argent_account_snip9_compatibility(
    argent_account: BaseAccount,
):
    result = await argent_account.supports_interface(SNIP9InterfaceVersion.V1)
    assert result is True
    result = await argent_account.supports_interface(SNIP9InterfaceVersion.V2)
    assert result is False


@pytest.mark.asyncio
async def test_account_outside_execution_any_caller(
    client,
    argent_account_class_hash,
    deployed_balance_contract,
    deploy_account_details_factory,
):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get(
        class_hash=argent_account_class_hash, argent_calldata=True
    )

    deploy_result = await Account.deploy_account_v1(
        address=address,
        class_hash=class_hash,
        salt=salt,
        key_pair=key_pair,
        client=client,
        constructor_calldata=[key_pair.public_key, 0],
        max_fee=MAX_FEE,
    )
    await deploy_result.wait_for_acceptance()
    account = deploy_result.account

    assert any(
        [
            await account.supports_interface(SNIP9InterfaceVersion.V1),
            await account.supports_interface(SNIP9InterfaceVersion.V2),
        ]
    )

    increase_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )

    call = await account.sign_outside_execution_call(
        calls=[
            increase_balance_call,
            increase_balance_call,
            increase_balance_call,
        ],
        execution_time_bounds=ExecutionTimeBounds(
            execute_after=datetime.datetime.now() - datetime.timedelta(hours=1),
            execute_before=datetime.datetime.now() + datetime.timedelta(hours=1),
        ),
        caller=ANY_CALLER,
    )

    tx = await account.execute_v1(calls=[call], max_fee=MAX_FEE)
    await account.client.wait_for_tx(tx.transaction_hash)


@pytest.mark.asyncio
async def test_account_outside_execution_for_invalid_caller(
    client,
    argent_account_class_hash,
    deployed_balance_contract,
    deploy_account_details_factory,
):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get(
        class_hash=argent_account_class_hash, argent_calldata=True
    )

    deploy_result = await Account.deploy_account_v1(
        address=address,
        class_hash=class_hash,
        salt=salt,
        key_pair=key_pair,
        client=client,
        constructor_calldata=[key_pair.public_key, 0],
        max_fee=MAX_FEE,
    )
    await deploy_result.wait_for_acceptance()
    account = deploy_result.account

    assert any(
        [
            await account.supports_interface(SNIP9InterfaceVersion.V1),
            await account.supports_interface(SNIP9InterfaceVersion.V2),
        ]
    )

    increase_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )

    call = await account.sign_outside_execution_call(
        calls=[
            increase_balance_call,
            increase_balance_call,
            increase_balance_call,
        ],
        execution_time_bounds=ExecutionTimeBounds(
            execute_after=datetime.datetime.now() - datetime.timedelta(hours=1),
            execute_before=datetime.datetime.now() + datetime.timedelta(hours=1),
        ),
        caller=deployed_balance_contract.address,
    )

    tx = await account.execute_v1(calls=[call], max_fee=MAX_FEE)

    with pytest.raises(TransactionRevertedError) as err:
        await account.client.wait_for_tx(tx.transaction_hash)

    assert "argent/invalid-caller" in err.value.message


@pytest.mark.asyncio
async def test_account_outside_execution_for_impossible_timebounds(
    client,
    argent_account_class_hash,
    deployed_balance_contract,
    deploy_account_details_factory,
):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get(
        class_hash=argent_account_class_hash, argent_calldata=True
    )

    deploy_result = await Account.deploy_account_v1(
        address=address,
        class_hash=class_hash,
        salt=salt,
        key_pair=key_pair,
        client=client,
        constructor_calldata=[key_pair.public_key, 0],
        max_fee=MAX_FEE,
    )
    await deploy_result.wait_for_acceptance()
    account = deploy_result.account

    assert any(
        [
            await account.supports_interface(SNIP9InterfaceVersion.V1),
            await account.supports_interface(SNIP9InterfaceVersion.V2),
        ]
    )

    increase_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )

    call = await account.sign_outside_execution_call(
        calls=[
            increase_balance_call,
            increase_balance_call,
            increase_balance_call,
        ],
        execution_time_bounds=ExecutionTimeBounds(
            execute_after=datetime.datetime.now() - datetime.timedelta(days=10),
            execute_before=datetime.datetime.now() - datetime.timedelta(days=9),
        ),
        caller=ANY_CALLER,
    )

    tx = await account.execute_v1(calls=[call], max_fee=MAX_FEE)

    with pytest.raises(TransactionRevertedError) as err:
        await account.client.wait_for_tx(tx.transaction_hash)

    assert "argent/invalid-timestamp" in err.value.message
