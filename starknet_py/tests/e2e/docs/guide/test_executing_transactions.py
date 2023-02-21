import pytest


@pytest.mark.asyncio
async def test_executing_transactions(account, map_contract):
    # docs: start
    call = map_contract.functions["put"].prepare(key=20, value=20)

    resp = await account.execute(calls=call, max_fee=int(1e16))

    await account.client.wait_for_tx(resp.transaction_hash)
    # docs: end

    (value,) = await map_contract.functions["get"].call(key=20)
    assert value == 20
