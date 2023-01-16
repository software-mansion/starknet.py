import pytest

from starknet_py.contract import Contract
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


async def declare_contract(account: BaseAccount, compiled_contract: str):
    declare_result = await Contract.declare(
        account=account,
        compiled_contract=compiled_contract,
        max_fee=MAX_FEE,
    )
    await declare_result.wait_for_acceptance()


@pytest.mark.asyncio
async def test_pending_block(account, map_compiled_contract):
    await declare_contract(account, map_compiled_contract)

    blk = await account.client.get_block(block_number="pending")
    assert blk.block_hash


@pytest.mark.asyncio
async def test_latest_block(account, map_compiled_contract):
    await declare_contract(account, map_compiled_contract)

    blk = await account.client.get_block(block_number="latest")
    assert blk.block_hash
