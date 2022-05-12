import pytest
import subprocess

from typing import Tuple


def prepare_devnet(net: str) -> str:
    res = subprocess.run(
        [
            "./starknet_py/tests/e2e/setupy_scripts/prepare_devnet_for_gateway_test.sh",
            net,
        ],
        capture_output=True,
        text=True,
    )
    block_hash = res.stdout.splitlines()[-1]
    assert block_hash != ""
    return block_hash


@pytest.fixture(scope="module", autouse=True)
def run_prepared_devnet(run_devnet) -> Tuple[str, dict]:
    net = run_devnet
    args = {"block_hash": prepare_devnet(net)}
    yield net, args
