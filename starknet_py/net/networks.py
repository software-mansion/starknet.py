from typing import Union

MAINNET = "mainnet"
TESTNET = "testnet"

try:
    from typing import Literal

    PredefinedNetwork = Literal["mainnet", "testnet"]
except:
    PredefinedNetwork = str

Network = Union[PredefinedNetwork, str]


def net_address_from_net(net: Network) -> str:
    return {
        MAINNET: "https://alpha-mainnet.starknet.io",
        TESTNET: "https://alpha4.starknet.io",
    }.get(net, net)
