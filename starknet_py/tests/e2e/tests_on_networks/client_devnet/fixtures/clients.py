import pytest

from starknet_py.devnet_utils.devnet_client import DevnetClient


@pytest.fixture(name="devnet_client", scope="package")
def create_devnet_client(devnet) -> DevnetClient:
    return DevnetClient(node_url=devnet + "/rpc")
