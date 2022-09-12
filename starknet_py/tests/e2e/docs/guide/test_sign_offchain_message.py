import pytest


@pytest.mark.asyncio
async def test_sign_offchain_message():
    # pylint: disable=import-outside-toplevel, duplicate-code, unused-variable

    # add to docs: start
    from starknet_py.net import AccountClient, KeyPair
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.net.models import StarknetChainId
    from starknet_py.net.models.typed_data import Parameter, StarkNetDomain, TypedData

    # Create components of TypedData TypedDict
    starknet_domain = StarkNetDomain(name="StarkNet Mail", version="1", chainId=1)

    types = {
        "StarkNetDomain": [
            Parameter(name="name", type="felt"),
            Parameter(name="version", type="felt"),
            Parameter(name="chainId", type="felt"),
        ],
        "Person": [
            Parameter(name="name", type="felt"),
            Parameter(name="wallet", type="felt"),
        ],
        "Mail": [
            Parameter(name="from", type="Person"),
            Parameter(name="to", type="Person"),
            Parameter(name="contents", type="felt"),
        ],
    }

    message = {
        "from": {"name": "Cow", "wallet": "0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826"},
        "to": {"name": "Bob", "wallet": "0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB"},
        "contents": "Hello, Bob!",
    }

    # Create a TypedData dictionary
    typed_data = TypedData(
        types=types,
        primaryType="Mail",
        domain=starknet_domain,
        message=message,
    )

    # Create an AccountClient instance
    client = GatewayClient("testnet")
    account_client = AccountClient(
        client=client,
        address="0x7536539dbba2a49ab688a1c86332625f05f660a94908f362d29212e6071432d",
        chain=StarknetChainId.TESTNET,
        key_pair=KeyPair.from_private_key(
            2640601739596882773716581229189050365310622467205517187262055898295170952602
        ),
    )

    # We can calculate the message hash
    msg_hash = account_client.hash_message(typed_data=typed_data)

    # Sign the message
    signature = account_client.sign_message(typed_data=typed_data)

    # Verify the message
    assert await account_client.verify_message(
        typed_data=typed_data, signature=signature
    )
    # add to docs: end
