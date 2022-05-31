import pytest

from starknet_py.tests.e2e.utils import DevnetClientFactory


@pytest.mark.asyncio
async def test_sn_eth_messages(run_devnet):
    from starknet_py.net.l1.messages import (
        MessageToEth,
        MessageToEthContent,
    )
    from starknet_py.net.client import Client
    from starknet_py.net.models import StarknetChainId
    from starknet_py.net.networks import TESTNET

    ## All of the construction methods shown below are correct:

    # 1. From message content
    sn_to_eth_msg = MessageToEth.from_content(
        MessageToEthContent(
            starknet_sender="0x123123123",  # Either a hex SN address, or it's integer representation
            eth_recipient=123,  # Integer representation of Eth hex address
            payload=[123, 123],
        )
    )

    # 2. From message hash
    sn_to_eth_msg = MessageToEth.from_hash(
        (123).to_bytes(
            32, "big"
        )  # Provide 32 bytes as an input here, instead of message's content
    )

    client = Client(TESTNET)
    client = await DevnetClientFactory(run_devnet).make_devnet_client_without_account()

    tx_receipt = await client.get_transaction_receipt("0x123123123")

    print(tx_receipt)

    # sn_to_eth_msg = MessageToEth.from_tx_receipt(tx_receipt)

    sn_to_eth_msg = await MessageToEth.from_tx_hash(  # For sync version, use 'from_tx_hash_sync'
        "0x123123123", client
    )

    # count = sn_to_eth_msg.count_queued_sync(
    #     chain_id=StarknetChainId.TESTNET,
    #     endpoint_uri="https://my-rpc-endpoint.com/",  # Only HTTP RPC endpoints are supported for now
    #     block_number="pending"  # Block number or block representation literal
    # )