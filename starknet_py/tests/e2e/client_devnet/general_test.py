from typing import List

import pytest

from starknet_py.devnet_utils.devnet_client_models import PredeployedAccount
from starknet_py.net.client_models import PriceUnit


@pytest.mark.asyncio
async def test_mint(devnet_client, account):
    amount = 1000

    balance_before_mint = await account.get_balance()
    await devnet_client.mint(account.address, amount, PriceUnit.WEI)
    await devnet_client.mint(account.address, amount, "wei")
    await devnet_client.mint(account.address, amount, "WEI")
    await devnet_client.mint(account.address, amount)
    balance_after_mint = await account.get_balance()

    assert balance_after_mint == balance_before_mint + 4 * amount


@pytest.mark.asyncio
async def test_create_blocks(devnet_client):
    block_hash = await devnet_client.create_block()
    assert block_hash is not None


@pytest.mark.asyncio
async def test_abort_blocks(devnet_client):
    block_hash = await devnet_client.create_block()
    for _ in range(5):
        await devnet_client.create_block()

    aborted_blocks = await devnet_client.abort_block(block_hash=block_hash)
    assert len(aborted_blocks) == 6


@pytest.mark.asyncio
async def test_predeployed_accounts(devnet_client):
    accounts = await devnet_client.get_predeployed_accounts()

    isinstance(accounts, List)
    assert len(accounts) > 0
    isinstance(accounts[0], PredeployedAccount)
