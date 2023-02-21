import pytest


@pytest.mark.asyncio
async def test_multicall(account, map_contract):
    # docs-contract-interface: start
    invoke_result = await map_contract.functions["put"].invoke(
        key=10, value=20, max_fee=int(1e16)
    )

    await invoke_result.wait_for_acceptance()
    # docs-contract-interface: end

    (value,) = await map_contract.functions["get"].call(key=10)
    assert value == 20

    # docs-execute: start
    call = map_contract.functions["put"].prepare(key=20, value=20)

    resp = await account.execute(calls=call, max_fee=int(1e16))

    await account.client.wait_for_tx(resp.transaction_hash)
    # docs-execute: end

    (value,) = await map_contract.functions["get"].call(key=20)
    assert value == 20
