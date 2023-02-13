from dataclasses import dataclass
from typing import Literal, Optional, TypedDict, Union

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net.models import StarknetChainId

MAINNET = "mainnet"
TESTNET = "testnet"
TESTNET2 = "testnet2"

PredefinedNetwork = Literal["mainnet", "testnet", "testnet2"]


class CustomGatewayUrls(TypedDict):
    feeder_gateway_url: str
    gateway_url: str


@dataclass
class Network:
    address: Union[str, PredefinedNetwork, CustomGatewayUrls]
    chain_id: StarknetChainId

    def __init__(
        self,
        address: Union[str, PredefinedNetwork, CustomGatewayUrls],
        chain_id: Optional[StarknetChainId] = None,
    ):
        self.chain_id = chain_from_network(address, chain_id)
        self.address = address


def net_address_from_net(net: str) -> str:
    return {
        MAINNET: "https://alpha-mainnet.starknet.io",
        TESTNET: "https://alpha4.starknet.io",
        TESTNET2: "https://alpha4-2.starknet.io",
    }.get(net, net)


def default_token_address_for_network(net: Network) -> str:
    if net.address not in [TESTNET, TESTNET2, MAINNET]:
        raise ValueError(
            "Argument token_address must be specified when using a custom net address"
        )

    return FEE_CONTRACT_ADDRESS


def chain_from_network(
    net: Union[str, PredefinedNetwork, CustomGatewayUrls],
    chain: Optional[StarknetChainId] = None,
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
