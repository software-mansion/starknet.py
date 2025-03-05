from typing import AsyncGenerator

import pytest
import pytest_asyncio

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.full_node_ws_client import FullNodeWSClient
from starknet_py.net.ws_client import WSClient


@pytest.fixture(name="client", scope="package")
def create_full_node_client(devnet: str) -> FullNodeClient:
    return FullNodeClient(node_url=devnet + "/rpc")


@pytest_asyncio.fixture(scope="package")
async def ws_client(devnet_ws: str) -> AsyncGenerator[WSClient, None]:
    """
    Connects `WSClient` to devnet, returns its instance and disconnects after the tests.
    """
    client = WSClient(devnet_ws)

    await client.connect()
    yield client
    await client.disconnect()


@pytest_asyncio.fixture(scope="package")
async def full_node_ws_client(devnet_ws: str) -> AsyncGenerator[FullNodeWSClient, None]:
    """
    Connects `FullNodeWSClient` client to devnet, returns its instance and disconnects after the tests.
    """
    client = FullNodeWSClient(devnet_ws)

    await client.connect()
    yield client
    await client.disconnect()
