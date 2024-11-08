from typing import Generator

import pytest

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.full_node_ws_client import FullNodeWSClient


@pytest.fixture(name="client", scope="package")
def create_full_node_client(devnet) -> FullNodeClient:
    return FullNodeClient(node_url=devnet + "/rpc")


@pytest.fixture(scope="package")
async def full_node_ws_client(devnet_ws) -> Generator[str, None, None]:
    """
    Connects WebSocket client to devnet, returns its instance and disconnects after the tests.
    """
    ws_client = FullNodeWSClient(devnet_ws)

    await ws_client.connect()
    yield ws_client
    await ws_client.disconnect()
