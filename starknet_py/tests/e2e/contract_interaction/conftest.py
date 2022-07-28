from typing import List

import pytest
from starknet_py.tests.e2e.conftest import directory_with_contracts

PROXY_SOURCES = ["argent_proxy.cairo", "oz_proxy.cairo"]


@pytest.fixture(name="proxy_source")
def proxy_source(request) -> str:
    return (directory_with_contracts / request.param).read_text("utf-8")
