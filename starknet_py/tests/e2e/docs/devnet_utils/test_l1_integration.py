import pytest

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import ResourceBounds


@pytest.mark.skip(reason="Test require eth node running.")
@pytest.mark.asyncio
async def test_postman_load(devnet_client, l1_l2_contract, account):
    # pylint: disable=import-outside-toplevel
    # pylint: disable=unused-variable

    eth_account_address = 1390849295786071768276380950238675083608645509734

    # docs: start
    from starknet_py.devnet_utils.devnet_client import DevnetClient

    client = DevnetClient(node_url="http://127.0.0.1:5050")

    # docs: end
    client: DevnetClient = devnet_client
    # docs: start
    # Deploying the messaging contract on ETH network
    # e.g. anvil eth devnet https://github.com/foundry-rs/foundry/tree/master/crates/anvil
    await client.postman_load(network_url="http://127.0.0.1:8545")
    # docs: end

    # docs: messaging-contract-start
    from starknet_py.contract import Contract

    # Address of your contract that is emitting messages
    contract_address = "0x12345"

    # docs: messaging-contract-end
    contract_address = l1_l2_contract.address

    # docs: messaging-contract-start
    contract = await Contract.from_address(address=contract_address, provider=account)

    await contract.functions["increase_balance"].invoke_v3(
        user=account.address,
        amount=100,
        l1_resource_bounds=ResourceBounds(
            max_amount=50000, max_price_per_unit=int(1e12)
        ),
    )

    # docs: messaging-contract-end
    assert await contract.functions["get_balance"].call(user=account.address) == (100,)

    # docs: messaging-contract-start
    # Invoking function that is emitting message
    await contract.functions["withdraw"].invoke_v3(
        user=account.address,
        amount=100,
        l1_address=eth_account_address,
        l1_resource_bounds=ResourceBounds(
            max_amount=50000, max_price_per_unit=int(1e12)
        ),
    )
    # docs: messaging-contract-end
    assert await contract.functions["get_balance"].call(user=account.address) == (0,)

    # docs: flush-1-start
    # Sending messages from L2 to L1.
    flush_response = await client.postman_flush()

    message = flush_response.messages_to_l1[0]

    message_hash = await client.consume_message_from_l2(
        from_address=message.from_address,
        to_address=message.to_address,
        payload=message.payload,
    )
    # docs: flush-1-end

    # docs: send-l2-start
    await client.send_message_to_l2(
        l2_contract_address=contract_address,
        entry_point_selector=get_selector_from_name("deposit"),
        l1_contract_address="0xa000000000000000000000000000000000000001",
        payload=[account.address, 100],
        nonce="0x0",
        paid_fee_on_l1="0xfffffffffff",
    )

    # Sending messages from L1 to L2.
    flush_response = await client.postman_flush()
    # docs: send-l2-end

    assert await contract.functions["get_balance"].call(user=account.address) == (100,)
