import asyncio
from unittest.mock import Mock, MagicMock

import pytest
import web3


@pytest.mark.asyncio
async def test_eth_sn_messages():
    # pylint: disable=import-outside-toplevel, disable=duplicate-code, unused-variable
    # add to docs: start
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
    # add to docs: end

    w3 = Mock()
    w3.eth.wait_for_transaction_receipt.return_value = [0]

    # add to docs: start
    tx_receipt = w3.eth.wait_for_transaction_receipt("0x123123123")
    # add to docs: end

    MessageToStarknet.from_tx_receipt = MagicMock()
    MessageToStarknet.from_tx_receipt.return_value = [0]

    from_tx_hash_result = asyncio.Future()
    from_tx_hash_result.set_result(MagicMock())
    MessageToStarknet.from_tx_hash = MagicMock()
    MessageToStarknet.from_tx_hash.return_value = from_tx_hash_result

    MessageToStarknet.count_queued_sync = MagicMock()

    # add to docs: start
    eth_to_sn_msg = MessageToStarknet.from_tx_receipt(tx_receipt, w3)

    # 4. From transaction hash (fetches the receipt for you)
    eth_to_sn_msg = await MessageToStarknet.from_tx_hash(  # For sync version, use 'from_tx_hash_sync'
        tx_hash="0x123123123", web3=w3
    )

    # After message construction, we can fetch queued messages count
    count = eth_to_sn_msg[0].count_queued_sync(
        chain_id=StarknetChainId.TESTNET,
        web3=w3,
        block_number="pending",  # Block number or block representation literal
    )
    # add to docs: end
