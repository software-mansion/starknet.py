from typing import Literal, Union

from starknet_py.constants import FEE_CONTRACT_ADDRESS

MAINNET = "mainnet"
TESTNET = "testnet"
PredefinedNetwork = Literal["mainnet", "testnet"]

Network = Union[PredefinedNetwork, str]


def default_token_address_for_network(net: Network) -> str:
    if net not in [TESTNET, MAINNET]:
        raise ValueError(
            "Argument token_address must be specified when using a custom net address"
        )

    return FEE_CONTRACT_ADDRESS
