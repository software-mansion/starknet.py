from typing import Generator

import pytest


@pytest.fixture(scope="package")
def devnet_ws(devnet: str) -> Generator[str, None, None]:
    """
    Returns WebSocket address of devnet.
    """
    yield devnet.replace("http", "ws") + "/ws"
