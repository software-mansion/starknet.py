import pytest

from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_multicall(account, deployed_balance_contract):
    # pylint: disable=import-outside-toplevel
    balance_contract = deployed_balance_contract
    (initial_balance,) = await balance_contract.functions["get_balance"].call()
    # docs: start
    from starknet_py.hash.selector import get_selector_from_name
    from starknet_py.net.client_models import Call

    increase_balance_by_20_call = Call(
        to_addr=balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[20],
    )
    calls = [increase_balance_by_20_call, increase_balance_by_20_call]

    # Execute one transaction with multiple calls
    resp = await account.execute_v3(
        calls=calls,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    await account.client.wait_for_tx(resp.transaction_hash)
    # docs: end

    (final_balance,) = await balance_contract.functions["get_balance"].call()
    assert final_balance == initial_balance + 40
