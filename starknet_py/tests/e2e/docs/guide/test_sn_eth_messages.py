import asyncio
from unittest.mock import MagicMock, Mock

import pytest
from starknet_py.tests.e2e.utils import DevnetClientFactory


@pytest.mark.asyncio
async def test_sn_eth_messages(run_devnet):
    # pylint: disable=import-outside-toplevel, disable=duplicate-code, unused-variable
    # add to docs: start
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

    # add to docs: end

    client = await DevnetClientFactory(run_devnet).make_devnet_client_without_account()

    # add to docs: start
    # 3. From l2 (StarkNet) transaction receipt (provided by starknet.py, like shown below)
    tx_receipt = await client.get_transaction_receipt("0x123123123")
    # add to docs: end

    MessageToEth.from_tx_receipt = MagicMock()
    MessageToEth.from_tx_receipt.return_value = [0]

    from_tx_hash_result = asyncio.Future()
    from_tx_hash_result.set_result(MagicMock())
    MessageToEth.from_tx_hash = MagicMock()
    MessageToEth.from_tx_hash.return_value = from_tx_hash_result

    MessageToEth.count_queued_sync = MagicMock()

    # add to docs: start
    sn_to_eth_msg = MessageToEth.from_tx_receipt(tx_receipt)

    # 4. From transaction hash (fetches the receipt for you)
    sn_to_eth_msg = await MessageToEth.from_tx_hash(
        "0x123123123", client
    )  # For sync version, use 'from_tx_hash_sync'

    # add to docs: end

    w3 = Mock()

    # add to docs: start
    # After message construction, we can fetch queued messages count
    count = sn_to_eth_msg[0].count_queued_sync(
        chain_id=StarknetChainId.TESTNET,
        web3=w3,
        block_number="pending",  # Block number or block representation literal
    )
    # add to docs: end
