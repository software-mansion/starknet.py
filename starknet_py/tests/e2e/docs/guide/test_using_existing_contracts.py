import pytest

from starknet_py.net import AccountClient

# docs-abi: start
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
# docs-abi: end


@pytest.mark.asyncio
async def test_using_existing_contracts(
    gateway_client, gateway_account_client, erc20_contract
):
    # pylint: disable=import-outside-toplevel,too-many-locals,unused-variable
    # docs: start
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.contract import Contract
    from starknet_py.net.networks import TESTNET
    from starknet_py.net.models import StarknetChainId

    address = "0x00178130dd6286a9a0e031e4c73b2bd04ffa92804264a25c1c08c1612559f458"
    client = GatewayClient(TESTNET)
    # docs: end
    client = gateway_client
    # docs: start

    contract = Contract(address=address, abi=abi, client=gateway_client)
    # or
    acc_client = await AccountClient.create_account(
        client=gateway_client, chain=StarknetChainId.TESTNET
    )
    # docs: end

    acc_client = gateway_account_client

    address = erc20_contract.address

    # docs: start

    sender = "321"
    recipient = "123"

    contract = await Contract.from_address(client=acc_client, address=address)

    # Using only positional arguments
    invocation = await contract.functions["transferFrom"].invoke(
        sender, recipient, 10000, max_fee=int(1e16)
    )
    # docs: end
    await invocation.wait_for_acceptance()
    # docs: start

    # Using only keyword arguments
    invocation = await contract.functions["transferFrom"].invoke(
        sender=sender, recipient=recipient, amount=10000, max_fee=int(1e16)
    )
    # docs: end
    await invocation.wait_for_acceptance()
    # docs: start

    # Mixing positional with keyword arguments
    invocation = await contract.functions["transferFrom"].invoke(
        sender, recipient, amount=10000, max_fee=int(1e16)
    )
    # docs: end
    await invocation.wait_for_acceptance()
    # docs: start

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
    # docs: end

    assert balance == 200
