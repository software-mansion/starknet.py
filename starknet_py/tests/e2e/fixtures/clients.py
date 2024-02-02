import pytest

from starknet_py.net.full_node_client import FullNodeClient


@pytest.fixture(name="client", scope="package")
def create_full_node_client(network: str) -> FullNodeClient:
    return FullNodeClient(node_url=network + "/rpc")
