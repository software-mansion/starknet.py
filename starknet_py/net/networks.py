from typing import Union
import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

MAINNET = "mainnet"
TESTNET = "testnet"

try:
    # noinspection PyUnresolvedReferences
    from typing import Literal  # pylint: disable=no-name-in-module

    PredefinedNetwork = Literal["mainnet", "testnet"]
except ImportError:
    PredefinedNetwork = str


class CustomGatewayUrls(TypedDict):
    feeder_gateway_url: str
    gateway_url: str


Network = Union[PredefinedNetwork, str, CustomGatewayUrls]


def net_address_from_net(net: Network) -> str:
    return {
        MAINNET: "https://alpha-mainnet.starknet.io",
        TESTNET: "https://alpha4.starknet.io",
    }.get(net, net)
