import pytest

from starknet_py.devnet.devnet_client import DevnetClient


@pytest.fixture(name="devnet_client", scope="package")
def create_devnet_client(devnet) -> DevnetClient:
    return DevnetClient(node_url=devnet + "/rpc")


@pytest.fixture(name="devnet_forking_mode_client", scope="package")
def create_devnet_forking_mode_client(devnet_forking_mode) -> DevnetClient:
    return DevnetClient(node_url=devnet_forking_mode + "/rpc")
