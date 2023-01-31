import pytest


@pytest.mark.asyncio
async def test_signing_fee_estimate(gateway_account, map_contract):
    account = gateway_account
    # docs: start
    # Create a transaction
    call = map_contract.functions["put"].prepare(key=10, value=20)
    transaction = await account.sign_invoke_transaction(calls=call, max_fee=0)

    # Re-sign a transaction for fee estimation
    estimate_transaction = await account.sign_for_fee_estimate(transaction)

    # Transaction uses a version that cannot be executed on StarkNet
    assert estimate_transaction.version == 1 + 2**128
    assert estimate_transaction.signature != transaction.signature

    # Get a fee estimate
    estimate = await account.client.estimate_fee(transaction)
    assert estimate.overall_fee > 0

    # Use a new fee in original transaction
    transaction = await account.sign_invoke_transaction(
        calls=call, max_fee=estimate.overall_fee
    )

    # Send a transaction
    result = await account.client.send_transaction(transaction)
    await account.client.wait_for_tx(result.transaction_hash)
    # docs: end
