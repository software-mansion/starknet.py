from typing import Literal, Union

MAINNET = "mainnet"
GOERLI = "goerli"
SEPOLIA_TESTNET = "sepolia_testnet"
SEPOLIA_INTEGRATION = "sepolia_integration"

PredefinedNetwork = Literal[
    "mainnet", "goerli", "sepolia_testnet", "sepolia_integration"
]

Network = Union[PredefinedNetwork, str]
