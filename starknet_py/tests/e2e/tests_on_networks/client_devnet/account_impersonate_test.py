import sys

import pytest

from starknet_py.contract import Contract
from starknet_py.net.client_errors import ClientError
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_impersonate_account(
    devnet_client_fork_mode, account_to_impersonate, f_string_contract
):
    await devnet_client_fork_mode.impersonate_account(
        address=account_to_impersonate.address
    )

    contract = await Contract.from_address(
        provider=account_to_impersonate, address=f_string_contract.address
    )

    invocation = await contract.functions["set_string"].invoke_v3(
        "test", resource_bounds=MAX_RESOURCE_BOUNDS
    )

    await devnet_client_fork_mode.stop_impersonate_account(
        address=account_to_impersonate.address
    )

    assert (
        invocation.invoke_transaction.sender_address == account_to_impersonate.address
    )


@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_auto_impersonate(
    devnet_client_fork_mode, account_to_impersonate, f_string_contract
):
    await devnet_client_fork_mode.auto_impersonate()

    contract = await Contract.from_address(
        provider=account_to_impersonate, address=f_string_contract.address
    )

    invocation = await contract.functions["set_string"].invoke_v3(
        "test", resource_bounds=MAX_RESOURCE_BOUNDS
    )

    await devnet_client_fork_mode.stop_auto_impersonate()

    assert (
        invocation.invoke_transaction.sender_address == account_to_impersonate.address
    )


@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_impersonated_account_should_fail(
    account_to_impersonate, f_string_contract
):
    contract = await Contract.from_address(
        provider=account_to_impersonate, address=f_string_contract.address
    )

    with pytest.raises(ClientError):
        await contract.functions["set_string"].invoke_v3("test", auto_estimate=True)
