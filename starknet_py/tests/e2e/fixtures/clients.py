from typing import AsyncGenerator

import pytest
import pytest_asyncio

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.websockets.websocket_client import WebsocketClient


@pytest.fixture(name="client", scope="package")
def create_full_node_client(devnet: str) -> FullNodeClient:
    return FullNodeClient(node_url=devnet + "/rpc")


@pytest.fixture(name="client_with_predeclared_argent", scope="package")
def create_full_node_client_with_predeclare_argent(
    devnet_with_predeclared_argent: str,
) -> FullNodeClient:
    return FullNodeClient(node_url=devnet_with_predeclared_argent + "/rpc")


@pytest_asyncio.fixture(scope="package")
async def websocket_client(devnet_ws: str) -> AsyncGenerator[WebsocketClient, None]:
    """
    Connects `WebsocketClient` client to devnet, returns its instance and disconnects after the tests.
    """
    client = WebsocketClient(devnet_ws)

    await client.connect()
    yield client
    await client.disconnect()
