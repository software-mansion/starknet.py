import os
import subprocess
from pathlib import Path
from ast import literal_eval
from typing import Tuple

import json
import pytest
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.net.client import Client
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.tests.e2e.conftest import directory_with_contracts

directory = os.path.dirname(__file__)

SCRIPT_PATH = Path(directory) / "prepare_devnet_for_gateway_test.sh"
CONTRACT_COMPILED = directory_with_contracts / "balance_compiled.json"
CONTRACT_ABI = directory_with_contracts / "balance_abi.json"


def prepare_devnet(net: str) -> dict:
    res = subprocess.run(
        [SCRIPT_PATH, net, CONTRACT_COMPILED, CONTRACT_ABI],
        check=False,
        capture_output=True,
        text=True,
    )
    block = res.stdout.splitlines()[-1]
    block = literal_eval(block)
    assert block != ""
    return block


@pytest.fixture(name="compiled_contract")
def fixture_compiled_contract() -> dict:
    with open(CONTRACT_COMPILED, encoding="utf-8") as compiled_contract_file:
        return json.loads(compiled_contract_file.read())


def get_class_hash(net: str, contract_address: str) -> str:
    script_path = Path(directory, "get_class_hash.sh")
    res = subprocess.run(
        [script_path, net, contract_address],
        check=False,
        capture_output=True,
        text=True,
    )
    return res.stdout


@pytest.fixture(name="block_with_deploy")
def fixture_block_with_deploy(run_prepared_devnet) -> dict:
    _, block = run_prepared_devnet
    return block


@pytest.fixture(name="block_with_deploy_hash")
def fixture_block_with_deploy_hash(block_with_deploy) -> int:
    return int(block_with_deploy["block_hash"], 16)


@pytest.fixture(name="block_with_deploy_number")
def fixture_block_with_deploy_number(block_with_deploy) -> int:
    return block_with_deploy["block_number"]


@pytest.fixture(name="block_with_deploy_root")
def fixture_block_with_deploy_root(block_with_deploy) -> int:
    return int(block_with_deploy["state_root"], 16)


@pytest.fixture(name="block_with_invoke_number")
def fixture_block_with_invoke_number() -> int:
    return 1


@pytest.fixture(name="devnet_address")
def fixture_devnet_address(run_prepared_devnet) -> str:
    devnet_address, _ = run_prepared_devnet
    return devnet_address


@pytest.fixture(name="invoke_transaction")
def fixture_invoke_transaction():
    return {
        "hash": 0x5A8995AE36F3A87CC217311EC9372CD16602BA0FC273F4AFD1508A627D81B30,
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
def fixture_deploy_transaction_hash():
    return 0x11C1C6731ACE34AB4A9137A82092F26ECE38E7428E5E2028DA587893AAE0E02


@pytest.fixture(name="declare_transaction_hash")
def fixture_declare_transaction_hash():
    return 0x77CCBA4DF42CF0F74A8EB59A96D7880FAE371EDCA5D000CA5F9985652C8A8ED


@pytest.fixture(name="contract_address")
def fixture_contract_address():
    return 0x043D95E049C7DECE86574A8D3FB5C0F9E4422F8A7FEC6D744F26006374642252


@pytest.fixture(name="balance_contract")
def fixture_balance_contract() -> str:
    return (directory_with_contracts / "balance_compiled.json").read_text("utf-8")


@pytest.fixture(name="class_hash")
def fixture_class_hash(run_prepared_devnet, contract_address) -> int:
    net, _ = run_prepared_devnet
    return int(
        get_class_hash(net=net, contract_address=hex(contract_address))
        .strip()
        .replace('"', ""),
        16,
    )


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
