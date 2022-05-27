import os
from pathlib import Path
import pytest
from starknet_py.tests.e2e.utils import DevnetClientFactory

directory = os.path.dirname(__file__)
map_source_code = Path(directory, "map.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_using_account_client(run_devnet):
    # pylint: disable=import-outside-toplevel, duplicate-code
    # add to docs: start
    from starknet_py.net import AccountClient
    from starknet_py.net.networks import TESTNET
    from starknet_py.contract import Contract

    # Creates an account on local network and returns an instance
    acc_client = await AccountClient.create_account(net=TESTNET)
    # add to docs: end

    acc_client = await DevnetClientFactory(run_devnet).make_devnet_client()

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
        await map_contract.functions["put"].invoke(k, v, max_fee=0)
    ).wait_for_acceptance()

    (resp,) = await map_contract.functions["get"].call(
        k
    )  # Retrieves the value, which is equal to 4324 in this case
    # add to docs: end

    assert resp == v
