from typing import List

import pytest
from starknet_py.tests.e2e.conftest import directory_with_contracts


@pytest.fixture(name="proxy_sources")
def fixture_proxy_sources() -> List[str]:
    sources = ("argent_proxy.cairo", "oz_proxy.cairo")
    return [(directory_with_contracts / src).read_text("utf-8") for src in sources]
