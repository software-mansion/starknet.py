from dataclasses import dataclass
from functools import reduce
from typing import List, Optional

from eth_utils import keccak
from hexbytes import HexBytes
from web3 import Web3
from web3.types import BlockIdentifier as EthBlockIdentifier


from starknet_py.net import Client
from starknet_py.net.l1.contracts import StarknetL1Contract
from starknet_py.net.l1.starknet_l1_abi import STARKNET_L1_ABI
from starknet_py.net.models import (
    StarknetChainId,
    AddressRepresentation,
    parse_address,
)

from starknet_py.utils.sync import add_sync_methods


def encode_packed(*args: List[int]) -> bytes:
    return reduce(
        lambda acc, x: acc + x,
        [x.to_bytes(32, byteorder="big", signed=False) for x in args],
    )


@dataclass
class MessageToEthContent:
    """A dataclass representing a message's payload (from Starknet to Ethereum)"""

    starknet_sender: AddressRepresentation
    eth_recipient: int  # Integer representation of l1 hex address
    payload: List[int]

    @property
    def hash(self):
        return keccak(
            encode_packed(
                parse_address(self.starknet_sender),
                self.eth_recipient,
                len(self.payload),
                *self.payload,
            )
        )


def int_from_hexbytes(hexb: HexBytes) -> int:
    return int(hexb.hex(), 16)


@add_sync_methods
@dataclass
class MessageToEth:
    """

    Class which enables you to check Starknet to Ethereum messages status
    """

    hash: bytes  # 32 bytes hash representation

    @classmethod
    def from_hash(cls, msg_hash: bytes) -> "MessageToEth":
        """

        :param msg_hash: Message's hash
        :return: Instance of `MessageToEth`
        """
        return cls(hash=msg_hash)

    @classmethod
    def from_content(cls, msg_content: MessageToEthContent) -> "MessageToEth":
        """

        :param msg_content: Dataclass representing message's content
        :return: Instance of `MessageToEth`
        """
        return cls.from_hash(msg_content.hash)

    @classmethod
    def from_tx_receipt(cls, tx_receipt) -> List["MessageToEth"]:
        """
        :param tx_receipt: A JSON from starknet.py's Client `get_transaction_receipt`
        :return: A list of Starknet to Ethereum messages
        """
        return [
            MessageToEth.from_content(
                MessageToEthContent(
                    starknet_sender=message["from_address"],
                    eth_recipient=int(message["to_address"], 16),
                    payload=[int(felt_str) for felt_str in message["payload"]],
                )
            )
            for message in tx_receipt["l2_to_l1_messages"]
        ]

    @classmethod
    async def from_tx_hash(
        cls,
        tx_hash: str,
        client: Client,
    ) -> List["MessageToEth"]:
        """

        :param tx_hash: A starknet transaction hash
        :param client: Instance of starknet.py's Client class
        :return: A list of messages to Ethereum in this transaction
        """
        receipt = await client.get_transaction_receipt(tx_hash)
        return cls.from_tx_receipt(receipt)

    def count_queued_sync(
        self,
        chain_id: StarknetChainId,
        web3: Web3,
        block_number: Optional[EthBlockIdentifier] = None,
    ) -> int:
        """

        :param chain_id: A `StarknetChainId` (which contains StarkNet core contract deployed)
        :param web3: Web3 instance from web3.py
        :param block_number: Optional. `EthBlockIdentifier` which is a hex address, integer,
                             or one of "latest", "earliest", "pending"
        :return: an integer (ranging from 0 upwards, representing the number of messages on L1 waiting for consumption)
        """
        return int_from_hexbytes(
            StarknetL1Contract(chain_id, web3).l2_to_l1_messages(
                self.hash, block_number
            )
        )


@dataclass
class MessageToStarknetContent:
    """A dataclass representing a Ethereum to Starknet message payload (from L1 to L2)"""

    eth_sender: int  # Integer representation of l1 hex address
    starknet_recipient: AddressRepresentation
    nonce: int
    selector: int
    payload: List[int]

    @property
    def hash(self):
        return keccak(
            encode_packed(
                self.eth_sender,
                parse_address(self.starknet_recipient),
                self.nonce,
                self.selector,
                len(self.payload),
                *self.payload,
            )
        )

    @classmethod
    def from_receipt(cls, receipt, web3: Web3) -> List["MessageToStarknetContent"]:
        logs = (
            web3.eth.contract(abi=STARKNET_L1_ABI)
            .events.LogMessageToL2()
            .processReceipt(receipt)
        )
        return [
            cls(
                eth_sender=int(log.args["from_address"], 16),
                starknet_recipient=log.args["to_address"],
                nonce=log.args["nonce"],
                selector=log.args["selector"],
                payload=log.args["payload"],
            )
            for log in logs
        ]


@add_sync_methods
@dataclass
class MessageToStarknet:
    """

    Class which enables you to check Eth -> Starknet (L1 -> L2) messages status
    """

    hash: bytes  # 32 bytes hash representation

    @classmethod
    def from_hash(cls, msg_hash: bytes) -> "MessageToStarknet":
        """

        :param msg_hash: Message's hash
        :return: Instance of `MessageToStarknet`
        """
        return cls(hash=msg_hash)

    @classmethod
    def from_content(cls, msg_content: MessageToStarknetContent) -> "MessageToStarknet":
        """

        :param msg_content: Dataclass representing message's content
        :return: Instance of `MessageToStarknet`
        """
        return cls.from_hash(msg_content.hash)

    @classmethod
    def from_tx_receipt(cls, receipt, web3: Web3) -> List["MessageToStarknet"]:
        """

        :param receipt: Transaction receipt object from web3.py
        :param web3: Web3 instance from web3.py
        :return: A list of message to Starknet (L1 to L2) messages in this receipt
        """
        return [
            cls.from_content(msg_content)
            for msg_content in MessageToStarknetContent.from_receipt(receipt, web3)
        ]

    @classmethod
    async def from_tx_hash(cls, tx_hash: str, web3: Web3) -> List["MessageToStarknet"]:
        """

        :param tx_hash: Transaction hash including some L1 to L2 messages
        :param web3: Web3 instance from web3.py
        :return: A list of messages to StarkNet in this transaction
        """
        receipt = web3.eth.getTransactionReceipt(tx_hash)
        return cls.from_tx_receipt(receipt, web3)

    def count_queued_sync(
        self,
        chain_id: StarknetChainId,
        web3: Web3,
        block_number: Optional[EthBlockIdentifier] = None,
    ) -> int:
        """

        :param chain_id: A `StarknetChainId` (which contains StarkNet core contract deployed)
        :param web3: Web3 instance from web3.py
        :param block_number: Optional. `EthBlockIdentifier` which is a hex address, integer,
                             or one of "latest", "earliest", "pending"
        :return: an integer (0 or 1, 0 meaning not received or a consumed message,
                 and 1 meaning a queued message waiting for consumer)
        """
        return int_from_hexbytes(
            StarknetL1Contract(chain_id, web3).l1_to_l2_messages(
                self.hash, block_number
            )
        )
