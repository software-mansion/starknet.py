import pytest

from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


@pytest.mark.asyncio
async def test_declare_tx(account, map_compiled_contract):
    declare_tx = await account.sign_declare_transaction(
        compiled_contract=map_compiled_contract, max_fee=MAX_FEE
    )
    result = await account.client.declare(declare_tx)

    await account.client.wait_for_tx(
        tx_hash=result.transaction_hash, wait_for_accept=True
    )
