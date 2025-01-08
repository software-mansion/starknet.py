import pytest

from starknet_py.net.client_models import ResourceBounds


@pytest.mark.asyncio
async def test_signing_fee_estimate(account, map_contract):
    # docs: start
    # Create a transaction
    call = map_contract.functions["put"].prepare_invoke_v3(key=10, value=20)
    transaction = await account.sign_invoke_v3(
        calls=call,
        l1_resource_bounds=ResourceBounds(max_amount=0, max_price_per_unit=0),
    )

    # Re-sign a transaction for fee estimation
    estimate_transaction = await account.sign_for_fee_estimate(transaction)

    # Transaction uses a version that cannot be executed on Starknet
    assert estimate_transaction.version == 3 + 2**128
    assert estimate_transaction.signature != transaction.signature

    # Get a fee estimation
    estimate = await account.client.estimate_fee(transaction)
    assert estimate.overall_fee > 0

    # Use a new fee in original transaction
    transaction = await account.sign_invoke_v3(
        calls=call, l1_resource_bounds=estimate.to_resource_bounds().l1_gas
    )

    # Send a transaction
    result = await account.client.send_transaction(transaction)
    await account.client.wait_for_tx(result.transaction_hash)
    # docs: end
