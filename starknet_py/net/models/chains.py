from enum import Enum
from typing import Optional

from starknet_py.common import int_from_bytes
from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net.networks import MAINNET, TESTNET, TESTNET2, Network


class StarknetChainId(Enum):
    MAINNET = int_from_bytes(b"SN_MAIN")
    TESTNET = int_from_bytes(b"SN_GOERLI")
    TESTNET2 = int_from_bytes(b"SN_GOERLI2")


def chain_from_network(
    net: Network, chain: Optional[StarknetChainId] = None
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


def default_token_address_for_chain(chain_id: Optional[StarknetChainId] = None) -> str:
    if chain_id not in [
        StarknetChainId.TESTNET,
        StarknetChainId.TESTNET2,
        StarknetChainId.MAINNET,
    ]:
        raise ValueError(
            "Argument token_address must be specified when using a custom network."
        )

    return FEE_CONTRACT_ADDRESS
