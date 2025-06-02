import pytest

from starknet_py.net.full_node_client import FullNodeClient


@pytest.fixture(name="client", scope="package")
def create_full_node_client(devnet) -> FullNodeClient:
    return FullNodeClient(node_url=devnet + "/rpc")


@pytest.fixture(name="client_fork_mode", scope="package")
def create_full_node_client_fork_mode(devnet_fork_mode) -> FullNodeClient:
    return FullNodeClient(node_url=devnet_fork_mode + "/rpc")
