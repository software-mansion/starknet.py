# pylint: disable=redefined-outer-name

import asyncio
import json
import subprocess
import time
from contextlib import closing
import socket
from typing import Generator

import pytest
import pytest_asyncio

from starknet_py.contract import Contract
from starknet_py.net import AccountClient
from starknet_py.tests.e2e.fixtures.constants import (
    TYPED_DATA_DIR,
    CONTRACTS_DIR,
)
from starknet_py.utils.data_transformer.data_transformer import CairoSerializer
from starknet_py.utils.typed_data import TypedData


# This fixture was added to enable using async fixtures
@pytest.fixture(scope="module")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


def pytest_addoption(parser):
    parser.addoption(
        "--net",
        action="store",
        default="devnet",
        help="Network to run tests on: possible 'testnet', 'devnet', 'all'",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--net") == "all":
        return

    run_testnet = config.getoption("--net") == "testnet"
    run_devnet = config.getoption("--net") == "devnet"
    for item in items:
        runs_on_testnet = "run_on_testnet" in item.keywords
        runs_on_devnet = "run_on_devnet" in item.keywords
        should_not_run = (runs_on_devnet and not run_devnet) or (
            runs_on_testnet and not run_testnet
        )
        if should_not_run:
            item.add_marker(pytest.mark.skip())


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


@pytest.fixture(scope="module")
def run_devnet() -> Generator[str, None, None]:
    """
    Runs devnet instance once per module and returns it's address
    """
    devnet_port, proc = start_devnet()
    yield f"http://localhost:{devnet_port}"
    proc.kill()


@pytest.fixture(scope="module")
def network(pytestconfig, run_devnet: str) -> str:
    """
    Returns network address depending on the --net parameter
    """
    net = pytestconfig.getoption("--net")
    net_address = {
        "devnet": run_devnet,
        "testnet": "testnet",
        "integration": "https://external.integration.starknet.io",
    }

    return net_address[net]


@pytest.fixture(
    name="typed_data",
    params=[
        "typed_data_example.json",
        "typed_data_felt_array_example.json",
        "typed_data_long_string_example.json",
        "typed_data_struct_array_example.json",
    ],
)
def typed_data(request) -> TypedData:
    """
    Returns TypedData dictionary example
    """
    file_name = getattr(request, "param")
    file_path = TYPED_DATA_DIR / file_name

    with open(file_path, "r", encoding="utf-8") as file:
        typed_data = json.load(file)

    return typed_data


@pytest_asyncio.fixture(name="cairo_serializer", scope="module")
async def cairo_serializer(gateway_account_client: AccountClient) -> CairoSerializer:
    """
    Returns CairoSerializer for "simple_storage_with_event.cairo"
    """
    client = gateway_account_client
    contract_content = (CONTRACTS_DIR / "simple_storage_with_event.cairo").read_text(
        "utf-8"
    )

    deployment_result = await Contract.deploy(
        client, compilation_source=contract_content
    )
    await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    return CairoSerializer(identifier_manager=contract.data.identifier_manager)
