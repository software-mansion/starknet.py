from dataclasses import dataclass
from typing import TypedDict, Union

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.net.models import StarknetChainId


class CustomGatewayUrls(TypedDict):
    feeder_gateway_url: str
    gateway_url: str


@dataclass(frozen=True)
class Network:
    """
    Dataclass describing the network.
    """

    address: Union[str, CustomGatewayUrls]
    chain_id: StarknetChainId


MAINNET = Network(
    address="https://alpha-mainnet.starknet.io", chain_id=StarknetChainId.MAINNET
)
TESTNET = Network(
    address="https://alpha4.starknet.io", chain_id=StarknetChainId.TESTNET
)
TESTNET2 = Network(
    address="https://alpha4-2.starknet.io", chain_id=StarknetChainId.TESTNET2
)


def default_token_address_for_network(net: Network) -> str:
    if net not in [MAINNET, TESTNET, TESTNET2]:
        raise ValueError(
            "Argument token_address must be specified when using a custom net address"
        )

    return FEE_CONTRACT_ADDRESS
