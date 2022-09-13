# pylint: disable=redefined-outer-name

import os
import subprocess
from pathlib import Path
from typing import Tuple, Dict

import pytest
import pytest_asyncio
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.gateway.transaction import (
    DEFAULT_DECLARE_SENDER_ADDRESS,
)

from starknet_py.net import AccountClient
from starknet_py.net.client import Client
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.tests.e2e.client.prepare_net_for_gateway_test import (
    prepare_net_for_tests,
    PreparedNetworkData,
)
from starknet_py.tests.e2e.conftest import directory_with_contracts

directory = os.path.dirname(__file__)


async def prepare_network(
    new_gateway_account_client: AccountClient,
) -> PreparedNetworkData:
    contract_compiled = Path(
        directory_with_contracts / "balance_compiled.json"
    ).read_text("utf-8")

    prepared_data = await prepare_net_for_tests(
        new_gateway_account_client, compiled_contract=contract_compiled
    )

    return prepared_data


def get_class_hash(net: str, contract_address: str) -> str:
    script_path = Path(directory, "get_class_hash.sh")
    res = subprocess.run(
        [script_path, net, contract_address],
        check=False,
        capture_output=True,
        text=True,
    )
    return res.stdout


@pytest.fixture(name="block_with_deploy_number")
def fixture_block_with_deploy_number(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> int:
    """
    Returns number of the block with deploy transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.block_with_deploy_number


@pytest.fixture(name="block_with_deploy_hash")
def fixture_block_with_deploy_hash(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> int:
    """
    Returns hash of the block with deploy transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.block_with_deploy_hash


@pytest.fixture(name="block_with_invoke_number")
def fixture_block_with_invoke_number(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> int:
    """
    Returns number of the block with invoke transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.block_with_invoke_number


@pytest.fixture(name="block_with_declare_number")
def fixture_block_with_declare_number(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> int:
    """
    Returns number of the block with declare transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.block_with_declare_number


@pytest.fixture(name="invoke_transaction")
def fixture_invoke_transaction(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> Dict:
    """
    Returns basic data of the InvokeFunction
    """
    _, prepared_data = prepare_network
    return {
        "hash": prepared_data.invoke_transaction_hash,
        "calldata": [1234],
        "entry_point_selector": get_selector_from_name("increase_balance"),
    }


@pytest.fixture(name="invoke_transaction_hash")
def fixture_invoke_transaction_hash(invoke_transaction: Dict) -> int:
    """
    Returns hash of the InvokeFunction
    """
    return invoke_transaction["hash"]


@pytest.fixture(name="invoke_transaction_calldata")
def fixture_invoke_transaction_calldata(invoke_transaction: Dict) -> int:
    """
    Returns calldata of the InvokeFunction
    """
    return invoke_transaction["calldata"]


@pytest.fixture(name="invoke_transaction_selector")
def fixture_invoke_transaction_selector(invoke_transaction: Dict) -> int:
    """
    Returns entry_point_selector of the InvokeFunction
    """
    return invoke_transaction["entry_point_selector"]


@pytest.fixture(name="deploy_transaction_hash")
def fixture_deploy_transaction_hash(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> int:
    """
    Returns hash of the DeployTransaction
    """
    _, prepared_data = prepare_network
    return prepared_data.deploy_transaction_hash


@pytest.fixture(name="declare_transaction_hash")
def fixture_declare_transaction_hash(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> int:
    """
    Returns hash of the DeclareTransaction
    """
    _, prepared_data = prepare_network
    return prepared_data.declare_transaction_hash


@pytest.fixture(name="contract_address")
def fixture_contract_address(prepare_network: Tuple[str, PreparedNetworkData]) -> int:
    """
    Returns an address of the deployed contract
    """
    _, prepared_data = prepare_network
    return prepared_data.contract_address


@pytest.fixture(name="balance_contract")
def fixture_balance_contract() -> str:
    """
    Returns compiled code of the balance.cairo contract
    """
    return (directory_with_contracts / "balance_compiled.json").read_text("utf-8")


@pytest.fixture(name="class_hash")
def fixture_class_hash(network: str, contract_address: int) -> int:
    """
    Returns class hash of the deployed contract
    """
    return int(
        get_class_hash(net=network, contract_address=hex(contract_address))
        .strip()
        .replace('"', ""),
        16,
    )


@pytest.fixture(name="clients")
def fixture_clients(network: str) -> Tuple[Client, Client]:
    """
    Returns Gateway and FullNode Clients
    """
    gateway_client = GatewayClient(net=network, chain=StarknetChainId.TESTNET)
    full_node_client = FullNodeClient(
        node_url=network + "/rpc",
        chain=StarknetChainId.TESTNET,
        net=network,
    )

    return gateway_client, full_node_client


@pytest_asyncio.fixture(name="prepare_network", scope="module", autouse=True)
async def fixture_prepare_network(
    network: str, new_gateway_account_client: AccountClient
) -> Tuple[str, PreparedNetworkData]:
    """
    Adds transactions to the network. Returns network address and PreparedNetworkData
    """
    net = network
    prepared_data = await prepare_network(new_gateway_account_client)
    yield net, prepared_data


@pytest.fixture(scope="module")
def sender_address(new_gateway_account_client: AccountClient) -> Dict:
    """
    Returns dict with DeclareTransaction sender_addresses depending on transaction version
    """
    return {0: DEFAULT_DECLARE_SENDER_ADDRESS, 1: new_gateway_account_client.address}
