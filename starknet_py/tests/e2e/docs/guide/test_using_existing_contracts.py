import os
from pathlib import Path
import pytest

from starknet_py.net import AccountClient

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
async def test_using_existing_contracts(gateway_client, account_client):
    # pylint: disable=import-outside-toplevel,too-many-locals,unused-variable
    # add to docs: start
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.contract import Contract
    from starknet_py.net.networks import TESTNET

    address = "0x00178130dd6286a9a0e031e4c73b2bd04ffa92804264a25c1c08c1612559f458"
    client = GatewayClient(TESTNET)
    # add to docs: end
    client = gateway_client
    # add to docs: start

    contract = Contract(address=address, abi=abi, client=gateway_client)
    # or
    acc_client = await AccountClient.create_account(client=gateway_client)
    # add to docs: end

    acc_client = account_client

    deployment_result = await Contract.deploy(
        client=account_client, compilation_source=erc20_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract
    address = contract.address

    # add to docs: start

    sender = "321"
    recipient = "123"

    contract = await Contract.from_address(client=acc_client, address=address)

    # Using only positional arguments
    invocation = await contract.functions["transferFrom"].invoke(
        sender, recipient, 10000, max_fee=int(1e16)
    )

    # Using only keyword arguments
    invocation = await contract.functions["transferFrom"].invoke(
        sender=sender, recipient=recipient, amount=10000, max_fee=int(1e16)
    )

    # Mixing positional with keyword arguments
    invocation = await contract.functions["transferFrom"].invoke(
        sender, recipient, amount=10000, max_fee=int(1e16)
    )

    # Creating a PreparedFunctionCall - creates a function call with arguments - useful for signing transactions and
    # specifying additional options
    transfer = contract.functions["transferFrom"].prepare(
        sender, recipient, amount=10000, max_fee=int(1e16)
    )
    invocation = await transfer.invoke()

    # Wait for tx
    await invocation.wait_for_acceptance()

    (balance,) = await contract.functions["balanceOf"].call(recipient)

    # You can also use key access, call returns NamedTuple
    result = await contract.functions["balanceOf"].call(recipient)
    balance = result.balance
    # add to docs: end

    assert balance == 200
