import pytest


@pytest.mark.asyncio
async def test_predeployd_accounts(devnet_client):
    accounts = await devnet_client.get_predeployed_accounts()
    assert len(accounts) > 0
