import os
import subprocess
from pathlib import Path
from typing import Tuple

import pytest

from starknet_py.tests.e2e.utils import DevnetClientFactory
from starknet_py.net.base_client import BaseClient


directory = os.path.dirname(__file__)


def prepare_devnet(net: str) -> str:
    script_path = Path(directory, "prepare_devnet_for_gateway_test.sh")
    contract_compiled = Path(directory, "balance_compiled.json")
    contract_abi = Path(directory, "balance_abi.json")

    res = subprocess.run(
        [
            script_path,
            net,
            contract_compiled,
            contract_abi
        ],
        check=False,
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


@pytest.fixture(name="block_hash")
def fixture_block_hash(run_prepared_devnet) -> str:
    _, args = run_prepared_devnet
    return args["block_hash"]


@pytest.fixture(name="devnet_address")
def fixture_devnet_address(run_prepared_devnet) -> str:
    devnet_address, _ = run_prepared_devnet
    return devnet_address


@pytest.fixture(name="clients")
async def fixture_clients(run_prepared_devnet) -> Tuple[BaseClient, BaseClient]:
    devnet_address, _ = run_prepared_devnet
    gateway_client = await DevnetClientFactory(
        devnet_address
    ).make_devnet_client_without_account()
    full_node_client = await DevnetClientFactory(devnet_address).make_rpc_client()
    return gateway_client, full_node_client


@pytest.fixture()
def invoke_transaction_hash():
    return 0x5A8995AE36F3A87CC217311EC9372CD16602BA0FC273F4AFD1508A627D81B30


@pytest.fixture()
def deploy_transaction_hash():
    return 0x11C1C6731ACE34AB4A9137A82092F26ECE38E7428E5E2028DA587893AAE0E02


@pytest.fixture()
def contract_address():
    return 0x043D95E049C7DECE86574A8D3FB5C0F9E4422F8A7FEC6D744F26006374642252


@pytest.fixture()
def balance_contract() -> str:
    return Path(directory, "balance_compiled.json").read_text("utf-8")
