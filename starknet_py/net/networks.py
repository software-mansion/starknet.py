from typing import Union

MAINNET = "mainnet"
TESTNET = "testnet"

try:
    from typing import Literal  # pylint: disable=no-name-in-module

    PredefinedNetwork = Literal["mainnet", "testnet"]
except ImportError:
    PredefinedNetwork = str

Network = Union[PredefinedNetwork, str]


def net_address_from_net(net: Network) -> str:
    return {
        MAINNET: "https://alpha-mainnet.starknet.io",
        TESTNET: "https://alpha4.starknet.io",
    }.get(net, net)
