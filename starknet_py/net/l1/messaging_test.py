from unittest.mock import Mock
import pytest
import web3
from eth_abi.codec import ABICodec
from hexbytes import HexBytes
from web3._utils.abi import build_default_registry
from web3.datastructures import AttributeDict

from starknet_py.net.l1.messages import (
    MessageToStarknet,
    MessageToEth,
    MessageToStarknetContent,
    MessageToEthContent,
)
from starknet_py.net.models import StarknetChainId

# pylint: disable=redefined-outer-name

MOCK_MESSAGES_AMT = 123


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
async def test_messages_from_content(w3_mock):
    sn_to_eth = MessageToEth.from_content(
        MessageToEthContent(starknet_sender=123, eth_recipient=123, payload=[])
    ).count_queued_sync(
        chain_id=StarknetChainId.TESTNET,
        web3=w3_mock,
    )

    eth_to_sn = MessageToStarknet.from_content(
        MessageToStarknetContent(
            eth_sender=123,
            starknet_recipient=123,
            nonce=1,
            selector=123,
            payload=[],
        )
    ).count_queued_sync(chain_id=StarknetChainId.TESTNET, web3=w3_mock)

    assert sn_to_eth == MOCK_MESSAGES_AMT
    assert eth_to_sn == MOCK_MESSAGES_AMT


@pytest.mark.asyncio
async def test_messages_from_tx_hash(w3_mock):
    # L1 Mock
    w3_mock_receipt = web3.Web3(web3.EthereumTesterProvider())

    def get_tx_receipt(_tx_hash):
        return AttributeDict(
            {
                "blockHash": HexBytes(
                    0x69BD25B8733BB02EF6852F22769A1AB1F6A78F9BE211D5CFDD8FE4F1A9F8508B
                ),
                "blockNumber": 6269149,
                "contractAddress": None,
                "cumulativeGasUsed": 247068,
                "effectiveGasPrice": "0x9502f907",
                "from": "0x188412627e1d1f09ca84b66fa25caaa372489168",
                "gasUsed": 66418,
                "logs": [
                    AttributeDict(
                        {
                            "address": "0xde29d060D45901Fb19ED6C6e959EB22d8626708e",
                            "topics": [
                                HexBytes(
                                    "0x7D3450D4F5138E54DCB21A322312D50846EAD7856426FB38778F8EF33AECCC01"
                                ),
                                HexBytes(
                                    "0x000000000000000000000000D673399A9726BFAC06DE74873A2EB761437091EB"
                                ),
                                HexBytes(
                                    "0x01C8834570E523034EB2D4AC6FA75419DF0B6360C737DBEB98C81484561C6794"
                                ),
                                HexBytes(
                                    "0x01C8834570E523034EB2D4AC6FA75419DF0B6360C737DBEB98C81484561C6794"
                                ),
                            ],
                            "data": "0x000000000000000000000000000000000000000000000000000000000000004"
                            "0000000000000000000000000000000000000000000000000000000000000030f"
                            "00000000000000000000000000000000000000000000000000000000000000010"
                            "00000000000000000000000000000000000000000000000000000000000007b",
                            "blockNumber": 6269149,
                            "transactionHash": HexBytes(
                                "0x8847B3DD5FBC06B0DC5575417F4716F436BCAE66CA2C6B1316C45C490D9E5C9D"
                            ),
                            "transactionIndex": 2,
                            "blockHash": HexBytes(
                                "0x69BD25B8733BB02EF6852F22769A1AB1F6A78F9BE211D5CFDD8FE4F1A9F8508B"
                            ),
                            "logIndex": 4,
                            "removed": False,
                        }
                    )
                ],
                "logsBloom": HexBytes(
                    "0x00000000000000000000000800000000000000000000000000000000000"
                    "0000020000020000000000000000010000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000010000020000"
                    "0000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000400000000000002000000000000000000000"
                    "0800000000000000000000000000000000000800000000000000000000000"
                    "00000000000000000000088000"
                ),
                "status": 1,
                "to": "0x188412627e1d1f09ca84b66fa25caaa372489168",
                "transactionHash": HexBytes(
                    "0x8847B3DD5FBC06B0DC5575417F4716F436BCAE66CA2C6B1316C45C490D9E5C9D"
                ),
                "transactionIndex": 2,
                "type": "0x2",
            }
        )

    w3_mock_receipt.eth.getTransactionReceipt = get_tx_receipt

    mock_l2_client = Mock()
    # L2 Mock

    async def get_l2_tx_receipt(_tx_hash):
        return {
            "l2_to_l1_messages": [
                {
                    "from_address": "0x123123123",
                    "to_address": "0x123123123",
                    "payload": [str(MOCK_MESSAGES_AMT)],
                }
            ]
        }

    mock_l2_client.get_transaction_receipt = get_l2_tx_receipt

    sn_to_eth_msgs = await MessageToEth.from_tx_hash(
        tx_hash="0x123123123",
        client=mock_l2_client,
    )
    eth_to_sn_msgs = await MessageToStarknet.from_tx_hash(
        tx_hash="0x123123123",
        web3=w3_mock_receipt,
    )

    sn_to_eth_msgs_counts = [
        msg.count_queued_sync(
            chain_id=StarknetChainId.TESTNET,
            web3=w3_mock,
        )
        for msg in sn_to_eth_msgs
    ]

    eth_to_sn_msgs_counts = [
        msg.count_queued_sync(chain_id=StarknetChainId.TESTNET, web3=w3_mock)
        for msg in eth_to_sn_msgs
    ]

    assert sn_to_eth_msgs_counts == [MOCK_MESSAGES_AMT]
    assert eth_to_sn_msgs_counts == [MOCK_MESSAGES_AMT]
