import os
import pytest
from starknet_py.net.models import StarknetChainId

directory = os.path.dirname(__file__)


@pytest.mark.asyncio
async def test_using_account_client(
    run_devnet, gateway_account_client, map_source_code
):
    # pylint: disable=import-outside-toplevel, duplicate-code, too-many-locals
    # add to docs: start
    from starknet_py.net import AccountClient
    from starknet_py.contract import Contract
    from starknet_py.net.gateway_client import GatewayClient

    # add to docs: end
    testnet = run_devnet
    # add to docs: start

    # Creates an account on testnet and returns an instance
    client = GatewayClient(net=testnet)
    acc_client = await AccountClient.create_account(
        client=client, chain=StarknetChainId.TESTNET
    )
    # add to docs: end
    acc_client = gateway_account_client
    # add to docs: start

    # Deploy an example contract which implements a simple k-v store. Deploy transaction is not being signed.
    deployment_result = await Contract.deploy(
        client=acc_client, compilation_source=map_source_code
    )
    # Wait until deployment transaction is accepted
    await deployment_result.wait_for_acceptance()

    # Get deployed contract
    map_contract = deployment_result.deployed_contract
    k, v = 13, 4324
    # Adds a transaction to mutate the state of k-v store. The call goes through account proxy, because we've used
    # AccountClient to create the contract object
    await (
        await map_contract.functions["put"].invoke(k, v, max_fee=int(1e16))
    ).wait_for_acceptance()

    # Retrieves the value, which is equal to 4324 in this case
    (resp,) = await map_contract.functions["get"].call(k)

    # There is a possibility of invoking the multicall

    # Creates a list of prepared function calls
    calls = [
        map_contract.functions["put"].prepare(key=10, value=20),
        map_contract.functions["put"].prepare(key=30, value=40),
    ]

    # Executes only one transaction with prepared calls
    transaction_response = await acc_client.execute(calls=calls, max_fee=int(1e16))
    await acc_client.wait_for_tx(transaction_response.transaction_hash)
    # add to docs: end

    assert resp == v
