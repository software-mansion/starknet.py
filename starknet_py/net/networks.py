from typing import Literal, TypedDict, Union

from starknet_py.constants import FEE_CONTRACT_ADDRESS

MAINNET = "mainnet"
TESTNET = "testnet"
# TODO (#1178): remove that
TESTNET2 = "testnet2"

# TODO (#1178): remove that
PredefinedNetwork = Literal["mainnet", "testnet", "testnet2"]


class CustomGatewayUrls(TypedDict):
    feeder_gateway_url: str
    gateway_url: str


Network = Union[PredefinedNetwork, str, CustomGatewayUrls]


def net_address_from_net(net: str) -> str:
    return {
        MAINNET: "https://alpha-mainnet.starknet.io",
        TESTNET: "https://alpha4.starknet.io",
        # TODO (#1178): remove that
        TESTNET2: "https://alpha4-2.starknet.io",
    }.get(net, net)


def default_token_address_for_network(net: Network) -> str:
    # TODO (#1178): remove that
    if net not in [TESTNET, TESTNET2, MAINNET]:
        raise ValueError(
            "Argument token_address must be specified when using a custom net address"
        )

    return FEE_CONTRACT_ADDRESS
