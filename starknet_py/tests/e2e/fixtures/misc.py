# pylint: disable=redefined-outer-name

import json
from pathlib import Path

import pytest
import pytest_asyncio

from starknet_py.contract import Contract
from starknet_py.net import AccountClient
from starknet_py.net.models.typed_data import TypedData
from starknet_py.tests.e2e.fixtures.constants import (
    CONTRACTS_COMPILED_DIR,
    MAX_FEE,
    TYPED_DATA_DIR,
)
from starknet_py.utils.data_transformer.data_transformer import CairoSerializer


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


@pytest.fixture(scope="module")
def network(pytestconfig, run_devnet: str) -> str:
    """
    Returns network address depending on the --net parameter.
    """
    net = pytestconfig.getoption("--net")
    net_address = {
        "devnet": run_devnet,
        "testnet": "testnet",
        "integration": "https://external.integration.starknet.io",
    }

    return net_address[net]


@pytest.fixture(
    params=[
        "typed_data_example.json",
        "typed_data_felt_array_example.json",
        "typed_data_long_string_example.json",
        "typed_data_struct_array_example.json",
    ],
)
def typed_data(request) -> TypedData:
    """
    Returns TypedData dictionary example.
    """
    file_name = getattr(request, "param")
    file_path = TYPED_DATA_DIR / file_name

    with open(file_path, "r", encoding="utf-8") as file:
        typed_data = json.load(file)

    return typed_data


@pytest_asyncio.fixture(scope="module")
async def cairo_serializer(
    new_gateway_account_client: AccountClient,
) -> CairoSerializer:
    """
    Returns CairoSerializer for "simple_storage_with_event.cairo".
    """
    account = new_gateway_account_client
    compiled_contract = read_contract("simple_storage_with_event_compiled.json")

    declare_result = await Contract.declare(
        account=account, compiled_contract=compiled_contract, max_fee=MAX_FEE
    )
    await declare_result.wait_for_acceptance()
    deploy_result = await declare_result.deploy(max_fee=MAX_FEE)
    await deploy_result.wait_for_acceptance()

    contract = deploy_result.deployed_contract

    return CairoSerializer(identifier_manager=contract.data.identifier_manager)


def read_contract(file_name: str, *, directory: Path = CONTRACTS_COMPILED_DIR) -> str:
    """
    Return contents of file_name from directory.
    """
    return (directory / file_name).read_text("utf-8")
