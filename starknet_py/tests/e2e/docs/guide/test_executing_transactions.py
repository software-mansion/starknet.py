import pytest


@pytest.mark.asyncio
async def test_executing_transactions(account, map_contract):
    address = map_contract.address
    # docs: start
    # pylint: disable=import-outside-toplevel
    from starknet_py.hash.selector import get_selector_from_name
    from starknet_py.net.client_models import Call

    call = Call(
        to_addr=address, selector=get_selector_from_name("put"), calldata=[20, 20]
    )

    resp = await account.execute(calls=call, max_fee=int(1e16))

    await account.client.wait_for_tx(resp.transaction_hash)
    # docs: end

    (value,) = await map_contract.functions["get"].call(key=20)
    assert value == 20
