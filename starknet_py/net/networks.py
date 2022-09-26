from typing import TypedDict, Union, Literal

MAINNET = "mainnet"
TESTNET = "testnet"

PredefinedNetwork = Literal["mainnet", "testnet"]


class CustomGatewayUrls(TypedDict):
    feeder_gateway_url: str
    gateway_url: str


Network = Union[PredefinedNetwork, str, CustomGatewayUrls]


def net_address_from_net(net: str) -> str:
    return {
        MAINNET: "https://alpha-mainnet.starknet.io",
        TESTNET: "https://alpha4.starknet.io",
    }.get(net, net)
