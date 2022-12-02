from enum import Enum
from typing import Optional

from starknet_py.net.networks import Network, MAINNET, TESTNET, TESTNET2


class StarknetChainId(Enum):
    MAINNET = int.from_bytes(b"SN_MAIN", byteorder="big", signed=False)
    TESTNET = int.from_bytes(b"SN_GOERLI", byteorder="big", signed=False)
    TESTNET2 = int.from_bytes(b"SN_GOERLI2", byteorder="big", signed=False)


# Pyright ignores were added because it doesn't allow StarknetChainId as a type here.
# It is ok when it is used as type in a different module.
def chain_from_network(
    net: Network, chain: Optional[StarknetChainId]  # pyright: ignore
) -> StarknetChainId:  # pyright: ignore
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
