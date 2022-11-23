import pytest


@pytest.mark.asyncio
async def test_account_client_details(account_client, map_contract):
    # docs: start
    # There are two options of executing transactions
    # 1. Use contract interface

    await (
        await map_contract.functions["put"].invoke(key=10, value=20, max_fee=int(1e16))
    ).wait_for_acceptance()

    # 2. Use AccountClient's execute method

    call = map_contract.functions["put"].prepare(key=10, value=20)
    resp = await account_client.execute(calls=call, max_fee=int(1e16))
    await account_client.wait_for_tx(resp.transaction_hash)

    # The advantage of using the second approach is there can be more than only one call

    calls = [
        map_contract.functions["put"].prepare(key=10, value=20),
        map_contract.functions["put"].prepare(key=30, value=40),
        map_contract.functions["put"].prepare(key=50, value=60),
    ]
    # Executes one transaction with three calls
    resp = await account_client.execute(calls=calls, max_fee=int(1e16))
    await account_client.wait_for_tx(resp.transaction_hash)
    # docs: end

    (value,) = await map_contract.functions["get"].call(key=50)
    assert value == 60
