from enum import IntEnum
from typing import Optional

from starknet_py.common import int_from_bytes
from starknet_py.net.networks import MAINNET, SEPOLIA, SEPOLIA_INTEGRATION, Network


class StarknetChainId(IntEnum):
    """
    An enumeration representing Starknet chain IDs.
    """

    MAINNET = int_from_bytes(b"SN_MAIN")
    SEPOLIA = int_from_bytes(b"SN_SEPOLIA")
    SEPOLIA_INTEGRATION = int_from_bytes(b"SN_INTEGRATION_SEPOLIA")


def chain_from_network(
    net: Network, chain: Optional[StarknetChainId] = None
) -> StarknetChainId:
    mapping = {
        MAINNET: StarknetChainId.MAINNET,
        SEPOLIA: StarknetChainId.SEPOLIA,
        SEPOLIA_INTEGRATION: StarknetChainId.SEPOLIA_INTEGRATION,
    }

    if isinstance(net, str) and net in mapping:
        return mapping[net]

    if not chain:
        raise ValueError("Chain is required when not using predefined networks.")

    return chain
