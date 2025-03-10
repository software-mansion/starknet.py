import pytest

from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
@pytest.mark.skip("TODO(#1560)")
async def test_signing_fee_estimate(account, map_contract):
    # docs: start
    # Create a transaction
    call = map_contract.functions["put"].prepare_invoke_v3(key=10, value=20)
    transaction = await account.sign_invoke_v3(
        calls=call,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    # Re-sign a transaction for fee estimation
    estimate_transaction = await account.sign_for_fee_estimate(transaction)

    # Transaction uses a version that cannot be executed on Starknet
    assert estimate_transaction.version == 3 + 2**128
    assert estimate_transaction.signature != transaction.signature

    # Get a fee estimation
    estimate = await account.client.estimate_fee(transaction)
    assert estimate.overall_fee > 0
    print(estimate.overall_fee)
    print(estimate.to_resource_bounds())
    # Use a new fee in original transaction
    transaction = await account.sign_invoke_v3(
        calls=call, resource_bounds=estimate.to_resource_bounds()
    )

    # Send a transaction
    result = await account.client.send_transaction(transaction)
    await account.client.wait_for_tx(result.transaction_hash)
    # docs: end
