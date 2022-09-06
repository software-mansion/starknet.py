# pylint: disable=redefined-outer-name

import os
import subprocess
from pathlib import Path
from typing import Tuple

import pytest
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.net import AccountClient
from starknet_py.net.client import Client
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.tests.e2e.client.prepare_net_for_gateway_test import (
    prepare_net_for_tests,
)
from starknet_py.tests.e2e.conftest import directory_with_contracts

directory = os.path.dirname(__file__)


def prepare_network(gateway_account_client: AccountClient) -> dict:
    contract_compiled = Path(
        directory_with_contracts / "balance_compiled.json"
    ).read_text("utf-8")

    (
        contract_address,
        deploy_transaction_hash,
        block_with_deploy_number,
        block_with_deploy_hash,
        invoke_transaction_hash,
        block_with_invoke_number,
        declare_transaction_hash,
        block_with_declare_number,
    ) = prepare_net_for_tests(
        gateway_account_client, compiled_contract=contract_compiled
    )

    prepared_data = {
        "contract_address": contract_address,
        "deploy_transaction_hash": deploy_transaction_hash,
        "block_with_deploy_number": block_with_deploy_number,
        "block_with_deploy_hash": block_with_deploy_hash,
        "invoke_transaction_hash": invoke_transaction_hash,
        "block_with_invoke_number": block_with_invoke_number,
        "declare_transaction_hash": declare_transaction_hash,
        "block_with_declare_number": block_with_declare_number,
    }

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
def fixture_block_with_deploy_number(prepare_network) -> int:
    _, prepared_data = prepare_network
    return prepared_data["block_with_deploy_number"]


@pytest.fixture(name="block_with_deploy_hash")
def fixture_block_with_deploy_hash(prepare_network) -> int:
    _, prepared_data = prepare_network
    return prepared_data["block_with_deploy_hash"]


@pytest.fixture(name="block_with_invoke_number")
def fixture_block_with_invoke_number(prepare_network) -> int:
    _, prepared_data = prepare_network
    return prepared_data["block_with_invoke_number"]


@pytest.fixture(name="block_with_declare_number")
def fixture_block_with_declare_number(prepare_network) -> int:
    _, prepared_data = prepare_network
    return prepared_data["block_with_declare_number"]


@pytest.fixture(name="invoke_transaction")
def fixture_invoke_transaction(prepare_network):
    _, prepared_data = prepare_network
    return {
        "hash": prepared_data["invoke_transaction_hash"],
        "calldata": [1234],
        "entry_point_selector": get_selector_from_name("increase_balance"),
    }


@pytest.fixture(name="invoke_transaction_hash")
def fixture_invoke_transaction_hash(invoke_transaction):
    return invoke_transaction["hash"]


@pytest.fixture(name="invoke_transaction_calldata")
def fixture_invoke_transaction_calldata(invoke_transaction):
    return invoke_transaction["calldata"]


@pytest.fixture(name="invoke_transaction_selector")
def fixture_invoke_transaction_selector(invoke_transaction):
    return invoke_transaction["entry_point_selector"]


@pytest.fixture(name="deploy_transaction_hash")
def fixture_deploy_transaction_hash(prepare_network):
    _, prepared_data = prepare_network
    return prepared_data["deploy_transaction_hash"]


@pytest.fixture(name="declare_transaction_hash")
def fixture_declare_transaction_hash(prepare_network):
    _, prepared_data = prepare_network
    return prepared_data["declare_transaction_hash"]


@pytest.fixture(name="contract_address")
def fixture_contract_address(prepare_network):
    _, prepared_data = prepare_network
    return prepared_data["contract_address"]


@pytest.fixture(name="balance_contract")
def fixture_balance_contract() -> str:
    return (directory_with_contracts / "balance_compiled.json").read_text("utf-8")


@pytest.fixture(name="class_hash")
def fixture_class_hash(network, contract_address) -> int:
    return int(
        get_class_hash(net=network, contract_address=hex(contract_address))
        .strip()
        .replace('"', ""),
        16,
    )


@pytest.fixture(name="clients")
def fixture_clients(network) -> Tuple[Client, Client]:
    gateway_client = GatewayClient(net=network, chain=StarknetChainId.TESTNET)
    full_node_client = FullNodeClient(
        node_url=network + "/rpc",
        chain=StarknetChainId.TESTNET,
        net=network,
    )

    return gateway_client, full_node_client


# pylint: disable=redefined-outer-name
@pytest.fixture(name="prepare_network", scope="module", autouse=True)
def fixture_prepare_network(network, gateway_account_client) -> Tuple[str, dict]:
    net = network
    prepared_data = prepare_network(gateway_account_client)
    yield net, prepared_data
