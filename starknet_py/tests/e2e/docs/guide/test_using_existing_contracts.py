import os
from pathlib import Path
import pytest
from starknet_py.tests.e2e.utils import DevnetClientFactory

# add to docs: start | section abi
abi = [
    {
        "inputs": [
            {"name": "sender", "type": "felt"},
            {"name": "recipient", "type": "felt"},
            {"name": "amount", "type": "felt"},
        ],
        "name": "transferFrom",
        "outputs": [{"name": "success", "type": "felt"}],
        "type": "function",
    },
    {
        "inputs": [{"name": "account", "type": "felt"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "felt"}],
        "stateMutability": "view",
        "type": "function",
    },
]
# add to docs: end | section abi

directory = os.path.dirname(__file__)
erc20_source_code = Path(directory, "erc20.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_using_existing_contracts(run_devnet):
    # pylint: disable=import-outside-toplevel

    # add to docs: start
    from starknet_py.net.client import Client
    from starknet_py.contract import Contract
    from starknet_py.net.networks import TESTNET

    address = "0x00178130dd6286a9a0e031e4c73b2bd04ffa92804264a25c1c08c1612559f458"

    contract = Contract(address=address, abi=abi, client=Client(TESTNET))
    # or
    client = Client(TESTNET)
    # add to docs: end

    client = await DevnetClientFactory(run_devnet).make_devnet_client_without_account()

    deployment_result = await Contract.deploy(
        client=client, compilation_source=erc20_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    address = contract.address

    sender = "321"
    recipient = "123"

    # add to docs: start

    contract = await Contract.from_address(address, client)

    # Using only positional arguments
    invocation = await contract.functions["transferFrom"].invoke(
        sender, recipient, 10000, max_fee=0
    )

    # Using only keyword arguments
    invocation = await contract.functions["transferFrom"].invoke(
        sender=sender, recipient=recipient, amount=10000, max_fee=0
    )

    # Mixing positional with keyword arguments
    invocation = await contract.functions["transferFrom"].invoke(
        sender, recipient, amount=10000, max_fee=0
    )

    # Creating a PreparedFunctionCall - creates a function call with arguments - useful for signing transactions and
    # specifying additional options
    transfer = contract.functions["transferFrom"].prepare(
        sender, recipient, amount=10000, max_fee=0
    )
    await transfer.invoke()

    # Wait for tx
    await invocation.wait_for_acceptance()

    (balance,) = await contract.functions["balanceOf"].call(recipient)

    # You can also use key access, call returns NamedTuple
    result = await contract.functions["balanceOf"].call(recipient)
    balance = result.balance
    # add to docs: end

    assert balance == 200
