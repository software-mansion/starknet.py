from __future__ import annotations

import warnings
from enum import Enum
from typing import Optional

from starknet_py.common import int_from_bytes
from starknet_py.net.networks import MAINNET, TESTNET, TESTNET2, Network


class StarknetChainId(Enum):
    MAINNET = int_from_bytes(b"SN_MAIN")
    TESTNET = int_from_bytes(b"SN_GOERLI")
    TESTNET2 = int_from_bytes(b"SN_GOERLI2")

    @classmethod
    def from_network(cls, net: Network) -> StarknetChainId:
        """
        Create a chain from given network.
        :raises ValueError: when Network is unknown.
        :param net: Network of the chain.
        :return: StarknetChainId instance.
        """
        net_to_chain = {
            MAINNET: cls.MAINNET,
            TESTNET: cls.TESTNET,
            TESTNET2: cls.TESTNET2,
        }

        if not isinstance(net, str) or net not in net_to_chain:
            raise ValueError(
                f"Cannot create StarknetChainId from unknown Network '{net}'."
            )

        return net_to_chain[net]


def chain_from_network(
    net: Network, chain: Optional[StarknetChainId] = None
) -> StarknetChainId:
    warnings.warn(
        "Function chain_from_network is deprecated. Use StarknetChainId.from_network instead.",
        category=DeprecationWarning,
    )
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
