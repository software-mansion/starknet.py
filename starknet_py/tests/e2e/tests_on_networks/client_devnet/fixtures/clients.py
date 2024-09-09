import pytest

from starknet_py.devnet_utils.devnet_client import DevnetClient


@pytest.fixture(name="devnet_client", scope="package")
def create_devnet_client(devnet) -> DevnetClient:
    return DevnetClient(node_url=devnet + "/rpc")


@pytest.fixture(name="devnet_client_fork_mode", scope="package")
def create_devnet_client_fork_mode(devnet_forking_mode) -> DevnetClient:
    return DevnetClient(node_url=devnet_forking_mode + "/rpc")
