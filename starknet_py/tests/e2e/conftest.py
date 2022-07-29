import os
import time
import subprocess
import socket
from contextlib import closing
from pathlib import Path

import pytest

from starknet_py.net import KeyPair, AccountClient
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId, AddressRepresentation
from starknet_py.contract import Contract

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

PROXY_SOURCES = ["argent_proxy.cairo", "oz_proxy.cairo"]


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


@pytest.fixture(scope="function", autouse=True)
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


def create_account_client(
    address: AddressRepresentation, private_key: str, gateway_client: GatewayClient
):
    key_pair = KeyPair.from_private_key(int(private_key, 0))
    return AccountClient(
        address=address,
        client=gateway_client,
        key_pair=key_pair,
    )


@pytest.fixture(scope="function")
def address_and_private_key(pytestconfig):
    net = pytestconfig.getoption("--net")

    account_details = {
        "devnet": (DEVNET_ACCOUNT_ADDRESS, DEVNET_ACCOUNT_PRIVATE_KEY),
        "testnet": (TESTNET_ACCOUNT_ADDRESS, TESTNET_ACCOUNT_PRIVATE_KEY),
        "integration": (INTEGRATION_ACCOUNT_ADDRESS, INTEGRATION_ACCOUNT_PRIVATE_KEY),
    }

    return account_details[net]


@pytest.fixture(scope="function")
# pylint: disable=redefined-outer-name
def gateway_account_client(address_and_private_key, gateway_client):
    address, private_key = address_and_private_key

    return create_account_client(address, private_key, gateway_client)


@pytest.fixture(scope="function")
def rpc_account_client(address_and_private_key, rpc_client):
    address, private_key = address_and_private_key

    return create_account_client(address, private_key, rpc_client)


@pytest.fixture(scope="function")
def account_clients(gateway_account_client, rpc_account_client):
    return gateway_account_client, rpc_account_client


directory_with_contracts = Path(os.path.dirname(__file__)) / "mock_contracts_dir"


@pytest.fixture(scope="function")
def map_source_code():
    return (directory_with_contracts / "map.cairo").read_text("utf-8")


@pytest.fixture(scope="function")
def erc20_source_code():
    return (directory_with_contracts / "erc20.cairo").read_text("utf-8")


@pytest.fixture(name="map_contract", scope="function")
def deploy_map_contract(gateway_account_client, map_source_code) -> Contract:
    # pylint: disable=no-member
    deployment_result = Contract.deploy_sync(
        client=gateway_account_client, compilation_source=map_source_code
    )
    deployment_result = deployment_result.wait_for_acceptance_sync()
    return deployment_result.deployed_contract


@pytest.fixture(name="erc20_contract", scope="function")
def deploy_erc20_contract(gateway_account_client, erc20_source_code) -> Contract:
    # pylint: disable=no-member
    deployment_result = Contract.deploy_sync(
        client=gateway_account_client, compilation_source=erc20_source_code
    )
    deployment_result = deployment_result.wait_for_acceptance_sync()
    return deployment_result.deployed_contract


@pytest.fixture(name="proxy_source", scope="function")
def proxy_source(request) -> str:
    return (directory_with_contracts / request.param).read_text("utf-8")
