# pylint: disable=import-outside-toplevel, duplicate-code
import os
from pathlib import Path

import pytest

from starknet_py.tests.e2e.utils import DevnetClientFactory

directory = os.path.dirname(__file__)
map_source_code = Path(directory, "map.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_using_contract(run_devnet):
    # add to docs: start
    from starknet_py.contract import Contract
    from starknet_py.net.client import Client
    from starknet_py.net.networks import TESTNET

    client = Client(TESTNET)

    contract_address = (
        "0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b"
    )
    key = 1234
    # add to docs: end

    client = await DevnetClientFactory(run_devnet).make_devnet_client_without_account()

    deployment_result = await Contract.deploy(
        client=client, compilation_source=map_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract_address = contract.address

    # add to docs: start

    # Create contract from contract's address - Contract will download contract's ABI to know its interface.
    contract = await Contract.from_address(contract_address, client)
    # add to docs: end

    abi = contract.data.abi

    # add to docs: start

    # If the ABI is known, create the contract directly (this is the preferred way).
    contract = Contract(
        contract_address,
        abi,
        client,
    )

    # All exposed functions are available at contract.functions.
    # Here we invoke a function, creating a new transaction.
    invocation = await contract.functions["put"].invoke(key, 7, max_fee=0)

    # Invocation returns InvokeResult object. It exposes a helper for waiting until transaction is accepted.
    await invocation.wait_for_acceptance()

    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["get"].call(key)
    # saved = 7 now
    # add to docs: end

    assert saved == 7
