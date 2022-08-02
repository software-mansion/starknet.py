import pytest


@pytest.mark.asyncio
async def test_account_client_details(
    run_devnet, gateway_account_client, map_source_code
):
    # pylint: disable=import-outside-toplevel
    # add to docs: start
    from starknet_py.contract import Contract
    from starknet_py.net import AccountClient
    from starknet_py.net.models import StarknetChainId
    from starknet_py.net.gateway_client import GatewayClient

    net = "testnet"
    # add to docs: end
    net = run_devnet
    # add to docs: start

    # Creates an account
    client = await AccountClient.create_account(
        client=GatewayClient(net=net), chain=StarknetChainId.TESTNET
    )
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

    await contract.functions["put"].invoke(key=10, value=20, max_fee=int(1e16))

    # 2. Use AccountClient's execute method

    call = contract.functions["put"].prepare(key=10, value=20)
    await client.execute(calls=call, max_fee=int(1e16))

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
