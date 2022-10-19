import pytest


@pytest.mark.asyncio
async def test_sign_offchain_message(account_client):
    # pylint: disable=import-outside-toplevel, duplicate-code, unused-variable

    # add to docs: start
    # Create a TypedData dictionary
    typed_data = {
        "types": {
            "StarkNetDomain": [
                {"name": "name", "type": "felt"},
                {"name": "version", "type": "felt"},
                {"name": "chainId", "type": "felt"},
            ],
            "Person": [
                {"name": "name", "type": "felt"},
                {"name": "wallet", "type": "felt"},
            ],
            "Mail": [
                {"name": "from", "type": "Person"},
                {"name": "to", "type": "Person"},
                {"name": "contents", "type": "felt"},
            ],
        },
        "primaryType": "Mail",
        "domain": {"name": "StarkNet Mail", "version": "1", "chainId": 1},
        "message": {
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
    }

    # We can calculate the message hash
    msg_hash = account_client.hash_message(typed_data=typed_data)

    # Sign the message
    signature = account_client.sign_message(typed_data=typed_data)

    # Verify the message
    verify_result = await account_client.verify_message(
        typed_data=typed_data, signature=signature
    )
    # add to docs: end

    assert verify_result
