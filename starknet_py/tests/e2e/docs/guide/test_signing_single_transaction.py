# pylint: disable=import-outside-toplevel, too-many-locals, duplicate-code
import os
from pathlib import Path
import pytest
from starknet_py.tests.e2e.utils import DevnetClientFactory

directory = os.path.dirname(__file__)
contract_source_code = Path(directory, "balance.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_signing_single_transaction(run_devnet):
    # add to docs: start
    from starknet_py.utils.crypto.facade import sign_calldata
    from starknet_py.contract import Contract
    from starknet_py.net.client import Client
    from starknet_py.net.networks import TESTNET

    contract_address = (
        "0x00178130dd6286a9a0e031e4c73b2bd04ffa92804264a25c1c08c1612559f458"
    )
    private_key = 12345
    public_key = (
        1628448741648245036800002906075225705100596136133912895015035902954123957052
    )
    value = 340282366920938463463374607431768211583

    client = Client(TESTNET)
    # add to docs: end

    client = await DevnetClientFactory(run_devnet).make_devnet_client_without_account()

    deployment_result = await Contract.deploy(
        client=client, compilation_source=contract_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    contract_address = contract.address

    # add to docs: start

    contract = await Contract.from_address(contract_address, client)
    prepared = contract.functions["set_balance"].prepare(
        user=public_key, amount=value, max_fee=0
    )
    # Every transformed argument is stored in prepared.arguments
    # prepared.arguments = {"public_key": public_key, "amount": [127, 1]}

    signature = sign_calldata(prepared.arguments["amount"], private_key)
    invocation = await prepared.invoke(signature)
    await invocation.wait_for_acceptance()

    (stored,) = await contract.functions["get_balance"].call(public_key)
    assert stored == value
    # add to docs: end
