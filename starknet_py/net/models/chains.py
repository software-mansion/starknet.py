from typing import Optional

from starkware.starknet.definitions.general_config import (
    StarknetChainId as _StarknetChainId,
)

from starknet_py.net.networks import Network, MAINNET, TESTNET
from starknet_py.utils.docs import as_our_module

StarknetChainId = as_our_module(_StarknetChainId)


def chain_from_network(
    net: Network, chain: Optional[StarknetChainId]
) -> StarknetChainId:
    mapping = {
        MAINNET: StarknetChainId.MAINNET,
        TESTNET: StarknetChainId.TESTNET,
    }

    if net in mapping:
        return mapping[net]

    if not chain:
        raise ValueError("Chain is required when not using predefined networks.")

    return chain
