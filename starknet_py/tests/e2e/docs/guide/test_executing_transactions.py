import pytest


@pytest.mark.asyncio
async def test_executing_transactions(account, map_contract):
    address = map_contract.address
    # pylint: disable=import-outside-toplevel
    # docs: start
    from starknet_py.hash.selector import get_selector_from_name
    from starknet_py.net.client_models import (
        Call,
        ResourceBounds,
        ResourceBoundsMapping,
    )

    call = Call(
        to_addr=address, selector=get_selector_from_name("put"), calldata=[20, 20]
    )

    resp = await account.execute_v3(
        calls=call,
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17)),
            l1_data_gas=ResourceBounds(
                max_amount=int(1e5), max_price_per_unit=int(1e13)
            ),
        ),
    )

    await account.client.wait_for_tx(resp.transaction_hash)
    # docs: end

    call = Call(to_addr=address, selector=get_selector_from_name("get"), calldata=[20])
    (value,) = await account.client.call_contract(call)
    assert value == 20
