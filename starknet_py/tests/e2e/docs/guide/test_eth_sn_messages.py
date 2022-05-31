import asyncio
from unittest.mock import Mock, MagicMock, patch

import pytest
import web3
from eth_abi.codec import ABICodec
from web3._utils.abi import build_default_registry

from starknet_py.net.l1.messages import MessageToEth, MessageToEthContent
from starknet_py.net.l1.messaging_test import MOCK_MESSAGES_AMT


@pytest.fixture()
def w3_mock():
    mock_value = MOCK_MESSAGES_AMT.to_bytes(32, "big")

    mock_w3 = Mock()

    def mock_call(_tx, _bn) -> bytes:
        return mock_value

    mock_w3.eth.call = mock_call
    mock_w3.codec = ABICodec(build_default_registry())
    return mock_w3


@pytest.mark.asyncio
async def test_eth_sn_messages(w3_mock):
    from starknet_py.net.l1.messages import (
        MessageToStarknetContent,
        MessageToStarknet,
    )
    from starknet_py.net.models import StarknetChainId
    from starknet_py.contract import ContractFunction

    ## All of the construction methods shown below are correct:

    # 1. From message content
    eth_to_sn_msg = MessageToStarknet.from_content(
        MessageToStarknetContent(
            eth_sender=123,  # Integer representation of Eth hex address
            starknet_recipient="0x123123123",  # Either a hex SN address, or it's integer representation
            nonce=1,  # Can be retrieved from Eth transaction's receipt (the one containing the sent message)
            selector=ContractFunction.get_selector(
                "dummy_name"
            ),  # SN function selector based on function name
            payload=[32, 32, 32, 32],  # SN Function calldata, list of ints
        )
    )

    # 2. From message hash
    eth_to_sn_msg = MessageToStarknet.from_hash(
        (123).to_bytes(
            32, "big"
        )  # Provide 32 bytes as an input here, instead of message's content
    )

    # 3. From Eth transaction receipt (provided by web3.py, like shown below)
    w3 = web3.Web3(web3.providers.HTTPProvider("https://my-rpc-endpoint.com/"))

    w3 = Mock()
    w3.eth.wait_for_transaction_receipt.return_value = [0]

    tx_receipt = w3.eth.wait_for_transaction_receipt("0x123123123")

    with patch(
        "starknet_py.net.l1.messages.MessageToStarknet.from_tx_receipt", MagicMock()
    ) as from_tx_receipt, patch(
        "starknet_py.net.l1.messages.MessageToStarknet.from_tx_hash", MagicMock()
    ) as from_tx_hash, patch(
        "starknet_py.net.l1.messages.MessageToEth.count_queued_sync", MagicMock()
    ):

        from_tx_receipt.return_value = [0]

        from_tx_hash_result = asyncio.Future()
        from_tx_hash_result.set_result(MagicMock())
        from_tx_hash.return_value = from_tx_hash_result

        eth_to_sn_msg = MessageToStarknet.from_tx_receipt(tx_receipt, w3)

        # 4. From transaction hash (fetches the receipt for you)
        eth_to_sn_msg = await MessageToStarknet.from_tx_hash(  # For sync version, use 'from_tx_hash_sync'
            tx_hash="0x123123123", web3=w3
        )

        eth_to_sn_msg = MessageToEth.from_content(
            MessageToEthContent(starknet_sender=123, eth_recipient=123, payload=[])
        )

        # After message construction, we can fetch queued messages count
        count = eth_to_sn_msg.count_queued_sync(
            chain_id=StarknetChainId.TESTNET, web3=w3
        )
