import pytest

from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_create_call_from_contract(map_contract, account):
    # pylint: disable=import-outside-toplevel
    contract = map_contract

    client = account.client
    res = await map_contract.functions["put"].invoke_v3(
        # TODO(#1558): Use auto estimation
        key=1234,
        value=9999,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    await res.wait_for_acceptance()

    # docs: start
    from starknet_py.net.client_models import Call

    # Prepare a call through Contract
    call = contract.functions["get"].prepare_invoke_v3(key=1234)
    assert issubclass(type(call), Call)

    # Use call directly through Client
    result = await client.call_contract(call)
    # docs: end

    assert result[0] == 9999
