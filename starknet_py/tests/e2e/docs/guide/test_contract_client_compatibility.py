import pytest


@pytest.mark.asyncio
async def test_create_call_from_contract(map_contract, account):
    contract = map_contract
    max_fee = int(1e20)

    client = account.client
    res = await map_contract.functions["put"].invoke(
        key=1234, value=9999, auto_estimate=True
    )
    await res.wait_for_acceptance()

    # docs: start
    from starknet_py.net.client_models import Call

    # Prepare a call through Contract
    call = contract.functions["get"].prepare(key=1234)
    assert issubclass(type(call), Call)

    # Use call directly through Client
    result = await client.call_contract(call)
    # docs: end

    assert result[0] == 9999
