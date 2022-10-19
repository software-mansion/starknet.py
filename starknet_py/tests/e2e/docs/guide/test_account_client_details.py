import pytest


@pytest.mark.asyncio
async def test_account_client_details(gateway_account_client, map_source_code):
    # pylint: disable=import-outside-toplevel
    # add to docs: start
    from starknet_py.contract import Contract

    # add to docs: end
    client = gateway_account_client
    # add to docs: start

    # Deploys the contract
    deployment_result = await Contract.deploy(
        client, compilation_source=map_source_code
    )
    await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    # There are two options of executing transactions
    # 1. Use contract interface

    await (
        await contract.functions["put"].invoke(key=10, value=20, max_fee=int(1e16))
    ).wait_for_acceptance()

    # 2. Use AccountClient's execute method

    call = contract.functions["put"].prepare(key=10, value=20)
    resp = await client.execute(calls=call, max_fee=int(1e16))
    await client.wait_for_tx(resp.transaction_hash)

    # The advantage of using the second approach is there can be more than only one call

    calls = [
        contract.functions["put"].prepare(key=10, value=20),
        contract.functions["put"].prepare(key=30, value=40),
        contract.functions["put"].prepare(key=50, value=60),
    ]
    # Executes one transaction with three calls
    resp = await client.execute(calls=calls, max_fee=int(1e16))
    await client.wait_for_tx(resp.transaction_hash)
    # add to docs: end

    (value,) = await contract.functions["get"].call(key=50)
    assert value == 60
