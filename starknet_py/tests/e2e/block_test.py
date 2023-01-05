import pytest

from starknet_py.contract import Contract
from starknet_py.net import AccountClient
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


async def declare_contract(account_client: AccountClient, compiled_contract: str):
    declare_result = await Contract.declare(
        account=account_client,
        compiled_contract=compiled_contract,
        max_fee=MAX_FEE,
    )
    await declare_result.wait_for_acceptance()


@pytest.mark.asyncio
async def test_pending_block(new_gateway_account_client, map_compiled_contract):
    # TODO: change to new_account_client once devnet repaired
    await declare_contract(new_gateway_account_client, map_compiled_contract)

    blk = await new_gateway_account_client.get_block(block_number="pending")
    assert blk.block_hash


@pytest.mark.asyncio
async def test_latest_block(new_account_client, map_compiled_contract):
    await declare_contract(new_account_client, map_compiled_contract)

    blk = await new_account_client.get_block(block_number="latest")
    assert blk.block_hash
