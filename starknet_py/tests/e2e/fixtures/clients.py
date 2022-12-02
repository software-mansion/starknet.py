import sys
from typing import List

import pytest

from starknet_py.net.client import Client
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient


@pytest.fixture(name="gateway_client", scope="module")
def create_gateway_client(network: str) -> GatewayClient:
    """
    Creates and returns GatewayClient.
    """
    return GatewayClient(net=network)


@pytest.fixture(name="full_node_client", scope="module")
def create_full_node_client(network: str) -> FullNodeClient:
    """
    Creates and returns FullNodeClient.
    """
    return FullNodeClient(node_url=network + "/rpc", net=network)


def net_to_clients() -> List[str]:
    """
    Return client fixture names based on network in sys.argv.
    """
    clients = ["gateway_client"]
    nets = ["--net=integration", "--net=testnet", "testnet", "integration"]

    if set(nets).isdisjoint(sys.argv):
        clients.append("full_node_client")
    return clients


@pytest.fixture(
    scope="module",
    params=net_to_clients(),
)
def client(request) -> Client:
    """
    Returns Client instances.
    """
    return request.getfixturevalue(request.param)
