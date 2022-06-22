# pylint: disable=import-outside-toplevel, no-member, duplicate-code
import os
from pathlib import Path
import pytest

from starknet_py.tests.e2e.account.account_client_test import MAX_FEE
from starknet_py.tests.e2e.utils import DevnetClientFactory

directory = os.path.dirname(__file__)
map_source_code = Path(directory, "map.cairo").read_text("utf-8")


@pytest.mark.asyncio
def test_synchronous_api(run_devnet):
    # add to docs: start
    from starknet_py.contract import Contract
    from starknet_py.net import AccountClient

    client = AccountClient.create_account("testnet")

    contract_address = (
        "0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b"
    )
    # add to docs: end

    client = DevnetClientFactory(
        run_devnet
    ).make_devnet_client_from_predefined_account()

    deployment_result = Contract.deploy_sync(
        client=client, compilation_source=map_source_code
    )
    deployment_result = deployment_result.wait_for_acceptance_sync()
    contract = deployment_result.deployed_contract
    contract_address = contract.address

    # add to docs: start

    key = 1234
    contract = Contract.from_address_sync(contract_address, client)

    invocation = contract.functions["put"].invoke_sync(key, 7, max_fee=MAX_FEE)
    invocation.wait_for_acceptance_sync()

    (saved,) = contract.functions["get"].call_sync(key)  # 7
    # add to docs: end

    assert saved == 7
