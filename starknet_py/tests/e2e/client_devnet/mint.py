import pytest


@pytest.mark.asyncio
async def test_mint(devnet_client, devnet_account):
    amount = 1000

    balance_before_mint = await devnet_account.get_balance()
    await devnet_client.mint(hex(devnet_account.address), amount)
    balance_after_mint = await devnet_account.get_balance()

    assert balance_after_mint == balance_before_mint + amount
