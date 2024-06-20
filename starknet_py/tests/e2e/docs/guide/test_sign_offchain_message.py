import pytest

from starknet_py.utils.typed_data import Domain, Parameter


@pytest.mark.asyncio
async def test_sign_offchain_message(account):
    # pylint: disable=import-outside-toplevel, duplicate-code, unused-variable

    # docs: start
    from starknet_py.net.account.account import Account
    from starknet_py.net.full_node_client import FullNodeClient
    from starknet_py.net.models import StarknetChainId
    from starknet_py.net.signer.stark_curve_signer import KeyPair
    from starknet_py.utils.typed_data import TypedData

    # Create a TypedData dataclass instance
    typed_data = TypedData(
        types={
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
        },
        primary_type="Mail",
        domain=Domain(name="StarkNet Mail", version="1", chain_id=1),
        message={
            "from": {
                "name": "Cow",
                "wallet": "0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826",
            },
            "to": {
                "name": "Bob",
                "wallet": "0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB",
            },
            "contents": "Hello, Bob!",
        },
    )
    # docs: end

    # save account fixture
    account_fixture = account

    # docs: start

    # Create an Account instance
    client = FullNodeClient(node_url="your.node.url")
    account = Account(
        client=client,
        address="0x1111",
        key_pair=KeyPair(private_key=123, public_key=456),
        chain=StarknetChainId.SEPOLIA,
    )
    # docs: end

    # retrieve account
    account = account_fixture

    # docs: start

    # Sign the message
    signature = account.sign_message(typed_data=typed_data)

    # Verify the message
    verify_result = account.verify_message(typed_data=typed_data, signature=signature)

    # Or if just a message hash is needed
    message_hash = typed_data.message_hash(account.address)

    # docs: end

    assert verify_result
