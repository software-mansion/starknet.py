from dataclasses import dataclass
from functools import reduce
from typing import List, Optional
from eth_utils import keccak
from hexbytes import HexBytes
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.net.l1.contracts import StarknetL1Contract
from starknet_py.net.models import (
    StarknetChainId,
    EthBlockIdentifier,
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
class L1MessageContent:
    """A dataclass representing a message's payload (from L1 to L2)"""

    l2_sender: AddressRepresentation
    l1_recipient: int  # Integer representation of l1 hex address
    payload: List[int]

    @property
    def hash(self):
        return keccak(
            encode_packed(
                parse_address(self.l2_sender),
                self.l1_recipient,
                len(self.payload),
                *self.payload,
            )
        )


def int_from_hexbytes(hexb: HexBytes) -> int:
    return int(hexb.hex(), 16)


@add_sync_methods
@dataclass
class L1Message:
    """

    Class which enables you to check L2 -> L1 messages status
    """

    hash: bytes  # 32 bytes hash representation

    @classmethod
    def from_hash(cls, msg_hash: bytes) -> "L1Message":
        """

        :param msg_hash: Message's hash
        :return: Instance of `L1Message`
        """
        return cls(hash=msg_hash)

    @classmethod
    def from_content(cls, msg_content: L1MessageContent) -> "L1Message":
        """

        :param msg_content: Dataclass representing L1 message's content
        :return: Instance of `L1Message`
        """
        return cls.from_hash(msg_content.hash)

    async def count_queued(
        self,
        chain_id: StarknetChainId,
        endpoint_uri: str,
        block_number: Optional[EthBlockIdentifier] = None,
    ) -> int:
        """

        :param chain_id: A `StarknetChainId` (which contains StarkNet core contract deployed)
        :param endpoint_uri: Ethereum RPC URL (only HTTP endpoints are supported for now)
        :param block_number: Optional. `EthBlockIdentifier` which is a hex address, integer,
                             or one of "latest", "earliest", "pending"
        :return: an integer (ranging from 0 upwards, representing the number of messages on L1 waiting for consumption)
        """
        return int_from_hexbytes(
            await StarknetL1Contract(chain_id, endpoint_uri).l2_to_l1_messages(
                self.hash, block_number
            )
        )


@dataclass
class L2MessageContent:
    """A dataclass representing a message's payload (from L2 to L1)"""

    l1_sender: int  # Integer representation of l1 hex address
    l2_recipient: AddressRepresentation
    nonce: int
    function_name: str
    payload: List[int]

    @property
    def hash(self):
        return keccak(
            encode_packed(
                self.l1_sender,
                parse_address(self.l2_recipient),
                self.nonce,
                get_selector_from_name(self.function_name),
                len(self.payload),
                *self.payload,
            )
        )


@add_sync_methods
@dataclass
class L2Message:
    """

    Class which enables you to check L1 -> L2 messages status
    """

    hash: bytes  # 32 bytes hash representation

    @classmethod
    def from_hash(cls, msg_hash: bytes) -> "L2Message":
        """

        :param msg_hash: Message's hash
        :return: Instance of `L2Message`
        """
        return cls(hash=msg_hash)

    @classmethod
    def from_content(cls, msg_content: L2MessageContent) -> "L2Message":
        """

        :param msg_content: Dataclass representing L2 message's content
        :return: Instance of `L2Message`
        """
        return cls.from_hash(msg_content.hash)

    async def count_queued(
        self,
        chain_id: StarknetChainId,
        endpoint_uri: str,
        block_number: Optional[EthBlockIdentifier] = None,
    ) -> int:
        """

        :param chain_id: A `StarknetChainId` (which contains StarkNet core contract deployed)
        :param endpoint_uri: Ethereum RPC URL (only HTTP endpoints are supported for now)
        :param block_number: Optional. `EthBlockIdentifier` which is a hex address, integer,
                             or one of "latest", "earliest", "pending"
        :return: an integer (0 or 1, 0 meaning not received or a consumed message,
                 and 1 meaning a queued message waiting for consumer)
        """
        return int_from_hexbytes(
            await StarknetL1Contract(chain_id, endpoint_uri).l1_to_l2_messages(
                self.hash, block_number
            )
        )
