import pytest


@pytest.mark.asyncio
async def test_declare_tx(account_client, map_source_code):
    declare_tx = await account_client.sign_declare_transaction(
        compilation_source=map_source_code
    )
    result = await account_client.declare(declare_tx)

    await account_client.wait_for_tx(
        tx_hash=result.transaction_hash, wait_for_accept=True
    )


async def test_sign_declare_tx_fails_with_old_account(
    gateway_account_client, map_source_code
):
    with pytest.raises(ValueError) as exinfo:
        await gateway_account_client.sign_declare_transaction(
            compilation_source=map_source_code
        )

    assert (
        "Signing declare transactions is only supported with transaction version 1"
        in str(exinfo.value)
    )
