from typing import Literal, Union

from starknet_py.constants import FEE_CONTRACT_ADDRESS

MAINNET = "mainnet"
GOERLI = "goerli"
SEPOLIA_TESTNET = "sepolia_testnet"
SEPOLIA_INTEGRATION = "sepolia_integration"

PredefinedNetwork = Literal[
    "mainnet", "goerli", "sepolia_testnet", "sepolia_integration"
]

Network = Union[PredefinedNetwork, str]


def default_token_address_for_network(net: Network) -> str:
    if net not in [MAINNET, GOERLI, SEPOLIA_TESTNET, SEPOLIA_INTEGRATION]:
        raise ValueError(
            "Argument token_address must be specified when using a custom net address"
        )

    return FEE_CONTRACT_ADDRESS
