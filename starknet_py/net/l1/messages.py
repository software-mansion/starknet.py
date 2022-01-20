from dataclasses import dataclass
from functools import reduce
from typing import List
from eth_utils import keccak

from web3.providers import BaseProvider as L1Provider
from starknet_py.net.l1.contracts import StarknetL1Contract
from starknet_py.net.l1.networks import L1Network


def encode_packed(*args: List[int]) -> bytes:
    return reduce(
        lambda acc, x: acc + x,
        map(lambda x: x.to_bytes(32, byteorder="big", signed=False), args),
    )


@dataclass
class L1MessageContent:
    l2_sender: int
    l1_recipient: int
    payload: List[int]

    @property
    def hash(self):
        return keccak(
            encode_packed(
                self.l2_sender,
                self.l1_recipient,
                len(self.payload),
                *self.payload,
            )
        )


@dataclass
class L1Message:
    hash: int

    @classmethod
    def from_hash(cls, msg_hash: int) -> "L1Message":
        return cls(hash=msg_hash)

    @classmethod
    def from_content(cls, msg_content: L1MessageContent) -> "L1Message":
        return cls.from_hash(msg_content.hash)

    def get_status(self, l1_net: L1Network, l1_net_provider: L1Provider):
        return (
            StarknetL1Contract.on_l1_net(l1_net, l1_net_provider)
            .functions.l2ToL1Messages(self.hash)
            .call()
        )


@dataclass
class L2MessageContent:
    l1_sender: int
    l2_recipient: int
    nonce: int
    selector: int
    payload: List[int]

    @property
    def hash(self):
        return keccak(
            encode_packed(
                self.l1_sender,
                self.l2_recipient,
                self.nonce,
                self.selector,
                len(self.payload),
                *self.payload,
            )
        )


@dataclass
class L2Message:
    hash: int

    @classmethod
    def from_hash(cls, msg_hash: int) -> "L2Message":
        return cls(hash=msg_hash)

    @classmethod
    def from_content(cls, msg_content: L2MessageContent) -> "L2Message":
        return cls.from_hash(msg_content.hash)

    def get_status(self, l1_net_provider: L1Provider, l1_net: L1Network):
        return (
            StarknetL1Contract.on_l1_net(l1_net, l1_net_provider)
            .functions.l1ToL2Messages(self.hash)
            .call()
        )
