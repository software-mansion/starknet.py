from enum import Enum
from typing import Optional

from starknet_py.client.networks import MAINNET, TESTNET, TESTNET2, Network
from starknet_py.common import int_from_bytes


class StarknetChainId(Enum):
    MAINNET = int_from_bytes(b"SN_MAIN")
    TESTNET = int_from_bytes(b"SN_GOERLI")
    TESTNET2 = int_from_bytes(b"SN_GOERLI2")


def chain_from_network(
    net: Network, chain: Optional[StarknetChainId]
) -> StarknetChainId:
    mapping = {
        MAINNET: StarknetChainId.MAINNET,
        TESTNET: StarknetChainId.TESTNET,
        TESTNET2: StarknetChainId.TESTNET2,
    }

    if isinstance(net, str) and net in mapping:
        return mapping[net]

    if not chain:
        raise ValueError("Chain is required when not using predefined networks.")

    return chain
