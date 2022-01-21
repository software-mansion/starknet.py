from dataclasses import dataclass
from functools import reduce
from typing import List
from eth_utils import keccak
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.net import AsyncNet


from starknet_py.net.l1.contracts import StarknetL1Contract
from starknet_py.net.models import StarknetChainId
from starknet_py.utils.sync import add_sync_methods


def encode_packed(*args: List[int]) -> bytes:
    return reduce(
        lambda acc, x: acc + x,
        [x.to_bytes(32, byteorder="big", signed=False) for x in args],
    )


def get_async_provider(endpoint_uri: str):
    return Web3(
        AsyncHTTPProvider(endpoint_uri),
        modules={"eth": AsyncEth, "net": AsyncNet},
        middlewares=[],
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


@add_sync_methods
@dataclass
class L1Message:
    hash: int

    @classmethod
    async def from_hash(cls, msg_hash: int) -> "L1Message":
        return cls(hash=msg_hash)

    @classmethod
    async def from_content(cls, msg_content: L1MessageContent) -> "L1Message":
        return cls.from_hash(msg_content.hash)

    async def get_status(self, chain_id: StarknetChainId, endpoint_uri: str) -> int:
        provider = get_async_provider(endpoint_uri)
        return (
            StarknetL1Contract.on_l1_net(chain_id, provider)
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


@add_sync_methods
@dataclass
class L2Message:
    hash: int

    @classmethod
    async def from_hash(cls, msg_hash: int) -> "L2Message":
        return cls(hash=msg_hash)

    @classmethod
    async def from_content(cls, msg_content: L2MessageContent) -> "L2Message":
        return cls.from_hash(msg_content.hash)

    async def get_status(self, chain_id: StarknetChainId, endpoint_uri: str) -> int:
        provider = get_async_provider(endpoint_uri)
        return (
            StarknetL1Contract.on_l1_net(chain_id, provider)
            .functions.l1ToL2Messages(self.hash)
            .call()
        )
