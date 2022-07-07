import time
import subprocess
import socket
from contextlib import closing
from typing import Tuple

import pytest

from starknet_py.net.client import Client
from starknet_py.tests.e2e.client.conftest import prepare_devnet
from starknet_py.tests.e2e.utils import DevnetClientFactory


def pytest_addoption(parser):
    parser.addoption(
        "--net",
        action="store",
        default="devnet",
        help="Network to run tests on: possible 'testnet', 'devnet', 'all'",
    )


def get_available_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.getsockname()[1]


def start_devnet():
    devnet_port = get_available_port()

    command = [
        "poetry",
        "run",
        "starknet-devnet",
        "--host",
        "localhost",
        "--port",
        str(devnet_port),
        "--accounts",  # deploys specified number of accounts
        str(1),
        "--seed",  # generates same accounts each time
        str(1),
    ]
    # pylint: disable=consider-using-with
    proc = subprocess.Popen(command)
    time.sleep(5)
    return devnet_port, proc


@pytest.fixture(scope="module", autouse=True)
def run_devnet():
    devnet_port, proc = start_devnet()
    yield f"http://localhost:{devnet_port}"
    proc.kill()


def pytest_collection_modifyitems(config, items):
    if config.getoption("--net") == "all":
        return

    run_testnet = config.getoption("--net") == "testnet"
    for item in items:
        runs_on_testnet = "run_on_testnet" in item.keywords
        should_run = run_testnet == runs_on_testnet
        if not should_run:
            item.add_marker(pytest.mark.skip())


@pytest.fixture(name="clients")
async def fixture_clients(run_prepared_devnet) -> Tuple[Client, Client]:
    devnet_address, _ = run_prepared_devnet
    gateway_client = await DevnetClientFactory(
        devnet_address
    ).make_devnet_client_without_account()
    full_node_client = await DevnetClientFactory(devnet_address).make_rpc_client()
    return gateway_client, full_node_client


# pylint: disable=redefined-outer-name
@pytest.fixture(name="run_prepared_devnet", scope="module", autouse=True)
def fixture_run_prepared_devnet(run_devnet) -> Tuple[str, dict]:
    net = run_devnet
    block = prepare_devnet(net)
    yield net, block
