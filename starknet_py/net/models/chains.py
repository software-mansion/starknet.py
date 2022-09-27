from typing import Optional

from starkware.starknet.definitions.general_config import (
    StarknetChainId as _StarknetChainId,
)

from starknet_py.net.networks import Network, MAINNET, TESTNET
from starknet_py.utils.docs import as_our_module

StarknetChainId = as_our_module(_StarknetChainId)


# Pyright ignores were added because it doesn't allow StarknetChainId as a type here.
# It is ok when it is used as type in a different module.
def chain_from_network(
    net: Network, chain: Optional[StarknetChainId]  # pyright: ignore
) -> StarknetChainId:  # pyright: ignore
    mapping = {
        MAINNET: StarknetChainId.MAINNET,
        TESTNET: StarknetChainId.TESTNET,
    }

    if isinstance(net, str) and net in mapping:
        return mapping[net]

    if not chain:
        raise ValueError("Chain is required when not using predefined networks.")

    return chain
