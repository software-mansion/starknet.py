from enum import IntEnum
from typing import Optional

from starknet_py.common import int_from_bytes
from starknet_py.net.networks import MAINNET, TESTNET, Network


class StarknetChainId(IntEnum):
    """
    An enumeration representing Starknet chain IDs.
    """

    MAINNET = int_from_bytes(b"SN_MAIN")
    TESTNET = int_from_bytes(b"SN_GOERLI")


def chain_from_network(
    net: Network, chain: Optional[StarknetChainId] = None
) -> StarknetChainId:
    mapping = {
        MAINNET: StarknetChainId.MAINNET,
        TESTNET: StarknetChainId.TESTNET,
    }

    if isinstance(net, str) and net in mapping:
        return mapping[net]

    if not chain:
        raise ValueError("Chain is required when not using predefined networks.")

    return chain
