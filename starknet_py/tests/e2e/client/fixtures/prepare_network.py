# pylint: disable=redefined-outer-name
from typing import AsyncGenerator, Dict, List, Tuple

import pytest
import pytest_asyncio

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.contract import Contract
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.tests.e2e.client.fixtures.prepare_net_for_gateway_test import (
    PreparedNetworkData,
    prepare_net_for_tests,
)
from starknet_py.tests.e2e.fixtures.accounts import AccountToBeDeployedDetailsFactory
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.tests.e2e.fixtures.contracts_v1 import declare_contract
from starknet_py.tests.e2e.fixtures.misc import load_contract


@pytest_asyncio.fixture(scope="package")
async def balance_class_and_transaction_hash(account: BaseAccount) -> Tuple[int, int]:
    contract = load_contract("Balance")
    class_hash, transaction_hash = await declare_contract(
        account,
        contract["sierra"],
        contract["casm"],
    )
    return class_hash, transaction_hash


@pytest_asyncio.fixture(scope="package")
async def deployed_balance_contract(
    account: BaseAccount,
    balance_class_and_transaction_hash,
    balance_abi,
) -> Contract:
    class_hash, _ = balance_class_and_transaction_hash

    deploy_result = await Contract.deploy_contract_v3(
        account=account,
        abi=balance_abi,
        class_hash=class_hash,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    await deploy_result.wait_for_acceptance()

    return deploy_result.deployed_contract


@pytest_asyncio.fixture(scope="package")
async def deployed_balance_contract_2(
    account: BaseAccount,
    balance_class_and_transaction_hash,
    balance_abi,
) -> Contract:
    class_hash, _ = balance_class_and_transaction_hash
    deploy_result = await Contract.deploy_contract_v3(
        account=account,
        abi=balance_abi,
        class_hash=class_hash,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    await deploy_result.wait_for_acceptance()

    return deploy_result.deployed_contract


@pytest.fixture(scope="package")
def balance_abi() -> List:
    compiled_contract = create_sierra_compiled_contract(
        compiled_contract=load_contract("Balance")["sierra"]
    )
    assert compiled_contract.parsed_abi is not None
    return compiled_contract.parsed_abi


@pytest.fixture()
def block_with_invoke_number(prepare_network: Tuple[str, PreparedNetworkData]) -> int:
    """
    Returns number of the block with invoke transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.block_with_invoke_number


@pytest.fixture()
def block_with_declare_number(prepare_network: Tuple[str, PreparedNetworkData]) -> int:
    """
    Returns number of the block with declare transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.block_with_declare_number


@pytest.fixture()
def block_with_declare_hash(prepare_network: Tuple[str, PreparedNetworkData]) -> int:
    """
    Returns hash of the block with declare transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.block_with_declare_hash


@pytest.fixture()
def invoke_transaction(prepare_network: Tuple[str, PreparedNetworkData]) -> Dict:
    """
    Returns basic data of Invoke
    """
    _, prepared_data = prepare_network
    return {
        "hash": prepared_data.invoke_transaction_hash,
        "calldata": [1234],
        "entry_point_selector": get_selector_from_name("increase_balance"),
    }


@pytest.fixture()
def invoke_transaction_hash(invoke_transaction: Dict) -> int:
    """
    Returns hash of Invoke
    """
    return invoke_transaction["hash"]


@pytest.fixture()
def invoke_transaction_calldata(invoke_transaction: Dict) -> int:
    """
    Returns calldata of Invoke
    """
    return invoke_transaction["calldata"]


@pytest.fixture()
def invoke_transaction_selector(invoke_transaction: Dict) -> int:
    """
    Returns entry_point_selector of Invoke
    """
    return invoke_transaction["entry_point_selector"]


@pytest.fixture()
def declare_transaction_hash(prepare_network: Tuple[str, PreparedNetworkData]) -> int:
    """
    Returns hash of the DeclareTransaction
    """
    _, prepared_data = prepare_network
    return prepared_data.declare_transaction_hash


@pytest.fixture()
def contract_address(prepare_network: Tuple[str, PreparedNetworkData]) -> int:
    """
    Returns an address of the deployed contract
    """
    _, prepared_data = prepare_network
    return prepared_data.contract_address


# `contract_address` was used in other tests, which modified its storage values. This overlap
# caused test interdependencies, leading to inconsistent results in `test_get_storage_at`
# and `test_call_contract`, hence the introduction of `contract_address_2`.
@pytest.fixture()
def contract_address_2(prepare_network: Tuple[str, PreparedNetworkData]) -> int:
    """
    Returns an address of the deployed contract
    """
    _, prepared_data = prepare_network
    return prepared_data.contract_address_2


@pytest.fixture()
def class_hash(prepare_network: Tuple[str, PreparedNetworkData]) -> int:
    """
    Returns class hash of the deployed contract
    """
    _, prepared_data = prepare_network
    return prepared_data.class_hash


@pytest_asyncio.fixture(scope="package")
async def prepare_network(
    devnet,
    account: Account,
    deploy_account_details_factory: AccountToBeDeployedDetailsFactory,
    balance_class_and_transaction_hash: Tuple[int, int],
    deployed_balance_contract: Contract,
    deployed_balance_contract_2: Contract,
) -> AsyncGenerator[Tuple[str, PreparedNetworkData], None]:
    """
    Adds transactions to the network. Returns network address and PreparedNetworkData
    """
    net = devnet
    class_hash, transaction_hash = balance_class_and_transaction_hash
    details = await deploy_account_details_factory.get()

    prepared_data = await prepare_net_for_tests(
        account,
        deploy_account_details=details,
        transaction_hash=transaction_hash,
        contract=deployed_balance_contract,
        contract_2=deployed_balance_contract_2,
        declare_class_hash=class_hash,
    )

    yield net, prepared_data
