# pylint: disable=redefined-outer-name
import os
import subprocess
from pathlib import Path
from typing import AsyncGenerator, Dict, Tuple

import pytest
import pytest_asyncio
from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.net import AccountClient
from starknet_py.tests.e2e.client.fixtures.prepare_net_for_gateway_test import (
    PreparedNetworkData,
    prepare_net_for_tests,
)
from starknet_py.tests.e2e.fixtures.account_clients import (
    AccountToBeDeployedDetailsFactory,
)
from starknet_py.tests.e2e.fixtures.misc import read_contract
from starknet_py.tests.e2e.utils import AccountToBeDeployedDetails

directory = os.path.dirname(__file__)


async def prepare_network(
    new_gateway_account_client: AccountClient,
    deploy_account_details: AccountToBeDeployedDetails,
) -> PreparedNetworkData:
    contract_compiled = read_contract("balance_compiled.json")

    prepared_data = await prepare_net_for_tests(
        new_gateway_account_client,
        compiled_contract=contract_compiled,
        deploy_account_details=deploy_account_details,
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


@pytest.fixture(name="block_with_declare_hash")
def fixture_block_with_declare_hash(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> int:
    """
    Returns hash of the block with declare transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.block_with_declare_hash


@pytest.fixture(name="invoke_transaction")
def fixture_invoke_transaction(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> Dict:
    """
    Returns basic data of Invoke
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
    Returns hash of Invoke
    """
    return invoke_transaction["hash"]


@pytest.fixture(name="invoke_transaction_calldata")
def fixture_invoke_transaction_calldata(invoke_transaction: Dict) -> int:
    """
    Returns calldata of Invoke
    """
    return invoke_transaction["calldata"]


@pytest.fixture(name="invoke_transaction_selector")
def fixture_invoke_transaction_selector(invoke_transaction: Dict) -> int:
    """
    Returns entry_point_selector of Invoke
    """
    return invoke_transaction["entry_point_selector"]


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
    return read_contract("balance_compiled.json")


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


@pytest_asyncio.fixture(name="prepare_network", scope="module")
async def fixture_prepare_network(
    network: str,
    new_gateway_account_client: AccountClient,
    deploy_account_details_factory: AccountToBeDeployedDetailsFactory,
) -> AsyncGenerator[Tuple[str, PreparedNetworkData], None]:
    """
    Adds transactions to the network. Returns network address and PreparedNetworkData
    """
    net = network
    details = await deploy_account_details_factory.get()
    prepared_data = await prepare_network(new_gateway_account_client, details)
    yield net, prepared_data
