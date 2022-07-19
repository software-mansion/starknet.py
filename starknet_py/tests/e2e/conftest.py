import time
import subprocess
import socket
from contextlib import closing
from typing import Tuple

import pytest

from starknet_py.net import KeyPair, AccountClient
from starknet_py.net.client import Client
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.tests.e2e.client.conftest import prepare_devnet


TESTNET_ACCOUNT_PRIVATE_KEY = (
    "0x5d6871223e9d2f6136f3913e8ccb6daae0b6b2a8452b39f92a1ddc5a76eed9a"
)
TESTNET_ACCOUNT_ADDRESS = (
    "0x7536539dbba2a49ab688a1c86332625f05f660a94908f362d29212e6071432d"
)

DEVNET_ACCOUNT_PRIVATE_KEY = "0xcd613e30d8f16adf91b7584a2265b1f5"
DEVNET_ACCOUNT_ADDRESS = (
    "0x7d2f37b75a5e779f7da01c22acee1b66c39e8ba470ee5448f05e1462afcedb4"
)

INTEGRATION_ACCOUNT_PRIVATE_KEY = (
    "0x5C09392256E68EA48445A9386668055418EAB5538ADBE4B12FD0FDC782C1A07"
)
INTEGRATION_ACCOUNT_ADDRESS = (
    "0x60D7C88541F969520E46D39EC7C9053451CFEDBC2EEB847B684981A22CD452E"
)


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


# pylint: disable=redefined-outer-name
def pytest_collection_modifyitems(config, items):
    if config.getoption("--net") == "all":
        return

    run_testnet = config.getoption("--net") == "testnet"
    run_devnet = config.getoption("--net") == "devnet"
    for item in items:
        runs_on_testnet = "run_on_testnet" in item.keywords
        runs_on_devnet = "run_on_devnet" in item.keywords
        should_run = run_testnet == runs_on_testnet or run_devnet == runs_on_devnet
        if not should_run:
            item.add_marker(pytest.mark.skip())


@pytest.fixture(name="clients")
def fixture_clients(run_prepared_devnet) -> Tuple[Client, Client]:
    devnet_address, _ = run_prepared_devnet
    gateway_client = GatewayClient(net=devnet_address, chain=StarknetChainId.TESTNET)
    full_node_client = FullNodeClient(
        node_url=devnet_address + "/rpc",
        chain=StarknetChainId.TESTNET,
        net=devnet_address,
    )
    return gateway_client, full_node_client


# pylint: disable=redefined-outer-name
@pytest.fixture(name="run_prepared_devnet", scope="module", autouse=True)
def fixture_run_prepared_devnet(run_devnet) -> Tuple[str, dict]:
    net = run_devnet
    block = prepare_devnet(net)
    yield net, block


@pytest.fixture(name="gateway_client", scope="function")
def create_gateway_client(pytestconfig, run_devnet):
    net = pytestconfig.getoption("--net")
    net_address = {
        "devnet": run_devnet,
        "testnet": "testnet",
        "integration": "https://external.integration.starknet.io",
    }

    return GatewayClient(net=net_address[net], chain=StarknetChainId.TESTNET)


@pytest.fixture(name="rpc_client", scope="function")
def create_rpc_client(run_devnet):
    return FullNodeClient(
        node_url=run_devnet + "/rpc", chain=StarknetChainId.TESTNET, net=run_devnet
    )


@pytest.fixture(name="account_client", scope="function")
# pylint: disable=redefined-outer-name
def create_account_client(pytestconfig, gateway_client):
    net = pytestconfig.getoption("--net")
    client = None

    if net == "testnet":
        key_pair = KeyPair.from_private_key(int(TESTNET_ACCOUNT_PRIVATE_KEY, 0))
        client = AccountClient(
            address=TESTNET_ACCOUNT_ADDRESS,
            client=gateway_client,
            key_pair=key_pair,
        )

    if net == "integration":
        key_pair = KeyPair.from_private_key(int(INTEGRATION_ACCOUNT_PRIVATE_KEY, 0))
        client = AccountClient(
            address=INTEGRATION_ACCOUNT_ADDRESS,
            client=gateway_client,
            key_pair=key_pair,
        )

    if net == "devnet":
        key_pair = KeyPair.from_private_key(int(DEVNET_ACCOUNT_PRIVATE_KEY, 0))
        client = AccountClient(
            address=DEVNET_ACCOUNT_ADDRESS,
            client=gateway_client,
            key_pair=key_pair,
        )

    return client
