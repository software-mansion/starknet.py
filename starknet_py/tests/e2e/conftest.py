# pylint: disable=redefined-outer-name

import asyncio
import json
import os
import socket
import subprocess
import time
from contextlib import closing
from pathlib import Path

import pytest
import pytest_asyncio
from starkware.crypto.signature.signature import get_random_private_key

from starknet_py.net import KeyPair, AccountClient
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.http_client import GatewayHttpClient
from starknet_py.net.models import StarknetChainId, AddressRepresentation
from starknet_py.contract import Contract
from starknet_py.transactions.deploy import make_deploy_tx
from starknet_py.utils.data_transformer.data_transformer import CairoSerializer
from starknet_py.utils.typed_data import TypedData

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

INTEGRATION_NEW_ACCOUNT_PRIVATE_KEY = "0x1"

INTEGRATION_NEW_ACCOUNT_ADDRESS = (
    "0X126FAB6AE8ACA83E2DD00B92F94F3402397D527798E18DC28D76B7740638D23"
)

directory_with_contracts = Path(os.path.dirname(__file__)) / "mock_contracts_dir"
mocks_dir = Path(os.path.dirname(__file__)) / "mocks"


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
def run_devnet():
    devnet_port, proc = start_devnet()
    yield f"http://localhost:{devnet_port}"
    proc.kill()


@pytest.fixture(scope="module")
def network(pytestconfig, run_devnet):
    net = pytestconfig.getoption("--net")
    net_address = {
        "devnet": run_devnet,
        "testnet": "testnet",
        "integration": "https://external.integration.starknet.io",
    }

    return net_address[net]


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


@pytest.fixture(name="gateway_client", scope="module")
def create_gateway_client(network):
    return GatewayClient(net=network)


@pytest.fixture(name="rpc_client", scope="module")
def create_rpc_client(run_devnet):
    return FullNodeClient(node_url=run_devnet + "/rpc", net=run_devnet)


def create_account_client(
    address: AddressRepresentation,
    private_key: str,
    gateway_client: GatewayClient,
    supported_tx_version: int,
):
    key_pair = KeyPair.from_private_key(int(private_key, 0))
    return AccountClient(
        address=address,
        client=gateway_client,
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
        supported_tx_version=supported_tx_version,
    )


async def devnet_account_details(network, gateway_client):
    devnet_account = await AccountClient.create_account(
        client=gateway_client, chain=StarknetChainId.TESTNET
    )

    http_client = GatewayHttpClient(network)
    await http_client.post(
        method_name="mint",
        payload={
            "address": hex(devnet_account.address),
            "amount": int(1e30),
        },
    )

    return hex(devnet_account.address), hex(devnet_account.signer.private_key)


@pytest_asyncio.fixture(scope="module")
async def address_and_private_key(pytestconfig, network, gateway_client):
    net = pytestconfig.getoption("--net")

    account_details = {
        "testnet": (TESTNET_ACCOUNT_ADDRESS, TESTNET_ACCOUNT_PRIVATE_KEY),
        "integration": (INTEGRATION_ACCOUNT_ADDRESS, INTEGRATION_ACCOUNT_PRIVATE_KEY),
    }

    if net == "devnet":
        return await devnet_account_details(network, gateway_client)
    return account_details[net]


@pytest.fixture(scope="module")
def gateway_account_client(address_and_private_key, gateway_client):
    address, private_key = address_and_private_key

    return create_account_client(
        address, private_key, gateway_client, supported_tx_version=0
    )


@pytest.fixture(scope="module")
def rpc_account_client(address_and_private_key, rpc_client):
    address, private_key = address_and_private_key

    return create_account_client(
        address, private_key, rpc_client, supported_tx_version=0
    )


async def new_devnet_account_details(network, gateway_client):
    private_key = get_random_private_key()

    key_pair = KeyPair.from_private_key(private_key)
    deploy_tx = make_deploy_tx(
        constructor_calldata=[key_pair.public_key],
        compiled_contract=(
            directory_with_contracts / "new_account_compiled.json"
        ).read_text("utf-8"),
    )

    result = await gateway_client.deploy(deploy_tx)
    await gateway_client.wait_for_tx(
        tx_hash=result.transaction_hash,
    )
    address = result.contract_address

    http_client = GatewayHttpClient(network)
    await http_client.post(
        method_name="mint",
        payload={
            "address": hex(address),
            "amount": int(1e30),
        },
    )

    return hex(address), hex(key_pair.private_key)


@pytest_asyncio.fixture(scope="module")
async def new_address_and_private_key(pytestconfig, network, gateway_client):
    net = pytestconfig.getoption("--net")

    account_details = {
        "testnet": None,
        "integration": (
            INTEGRATION_NEW_ACCOUNT_ADDRESS,
            INTEGRATION_NEW_ACCOUNT_PRIVATE_KEY,
        ),
    }

    if net == "devnet":
        return await new_devnet_account_details(network, gateway_client)
    return account_details[net]


@pytest.fixture(scope="module")
def new_gateway_account_client(new_address_and_private_key, gateway_client):
    address, private_key = new_address_and_private_key

    return create_account_client(
        address, private_key, gateway_client, supported_tx_version=1
    )


@pytest.fixture(
    scope="module",
    params=[
        "gateway_account_client",
        "new_gateway_account_client",
        "rpc_account_client",
    ],
)
def account_client(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(
    scope="module", params=["deploy_map_contract", "new_deploy_map_contract"]
)
def map_contract(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="module")
def map_source_code():
    return (directory_with_contracts / "map.cairo").read_text("utf-8")


@pytest.fixture(scope="module")
def erc20_source_code():
    return (directory_with_contracts / "erc20.cairo").read_text("utf-8")


@pytest_asyncio.fixture(name="deploy_map_contract", scope="module")
async def deploy_map_contract(gateway_account_client, map_source_code) -> Contract:
    deployment_result = await Contract.deploy(
        client=gateway_account_client, compilation_source=map_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    return deployment_result.deployed_contract


@pytest_asyncio.fixture(name="new_deploy_map_contract", scope="module")
async def new_deploy_map_contract(
    new_gateway_account_client, map_source_code
) -> Contract:
    deployment_result = await Contract.deploy(
        client=new_gateway_account_client, compilation_source=map_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    return deployment_result.deployed_contract


@pytest_asyncio.fixture(name="erc20_contract", scope="module")
async def deploy_erc20_contract(gateway_account_client, erc20_source_code) -> Contract:
    deployment_result = await Contract.deploy(
        client=gateway_account_client, compilation_source=erc20_source_code
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    return deployment_result.deployed_contract


@pytest.fixture(name="compiled_proxy")
def compiled_proxy(request) -> str:
    return (directory_with_contracts / request.param).read_text("utf-8")


@pytest.fixture(
    name="typed_data",
    params=["typed_data_example.json", "typed_data_struct_array_example.json"],
)
def typed_data(request) -> TypedData:
    file_name = getattr(request, "param")
    file_path = mocks_dir / file_name

    with open(file_path, "r", encoding="utf-8") as file:
        typed_data = json.load(file)

    return typed_data


@pytest_asyncio.fixture(name="cairo_serializer", scope="module")
async def cairo_serializer(gateway_account_client) -> CairoSerializer:
    client = gateway_account_client
    contract_content = (
        directory_with_contracts / "simple_storage_with_event.cairo"
    ).read_text("utf-8")

    deployment_result = await Contract.deploy(
        client, compilation_source=contract_content
    )
    await deployment_result.wait_for_acceptance()
    contract = deployment_result.deployed_contract

    return CairoSerializer(identifier_manager=contract.data.identifier_manager)
