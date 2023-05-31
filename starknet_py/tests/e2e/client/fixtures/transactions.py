# pylint: disable=redefined-outer-name
from typing import Tuple, cast

import pytest
import pytest_asyncio

from starknet_py.common import create_casm_class
from starknet_py.contract import Contract
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.account.account import Account
from starknet_py.net.client import Client
from starknet_py.net.models.transaction import DeclareV2, DeployAccount
from starknet_py.tests.e2e.client.fixtures.prepare_net_for_gateway_test import (
    PreparedNetworkData,
)
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR, MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import read_contract
from starknet_py.tests.e2e.utils import (
    get_deploy_account_details,
    get_deploy_account_transaction,
)


@pytest_asyncio.fixture(scope="package")
async def deploy_account_transaction(
    account_with_validate_deploy_class_hash: int, fee_contract: Contract, network: str
) -> DeployAccount:
    """
    Returns a DeployAccount transaction
    """
    address, key_pair, salt, class_hash = await get_deploy_account_details(
        class_hash=account_with_validate_deploy_class_hash, fee_contract=fee_contract
    )
    return await get_deploy_account_transaction(
        address=address,
        key_pair=key_pair,
        class_hash=class_hash,
        salt=salt,
        network=network,
    )


@pytest.fixture(scope="package")
def deploy_account_transaction_hash(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> int:
    """
    Returns hash of deploy account transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.deploy_account_transaction_hash


@pytest.fixture(scope="package")
def block_with_deploy_account_number(
    prepare_network: Tuple[str, PreparedNetworkData]
) -> int:
    """
    Returns number of the block with deploy account transaction
    """
    _, prepared_data = prepare_network
    return prepared_data.block_with_deploy_account_number


@pytest_asyncio.fixture(scope="package")
async def declare_v2_hello_starknet(gateway_account: Account) -> DeclareV2:
    """
    Returns DeclareV2 transaction.
    """
    hello_starknet_compiled = read_contract(
        "hello_starknet_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    compiled_class_hash = compute_casm_class_hash(
        create_casm_class(
            read_contract(
                "hello_starknet_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
            )
        )
    )
    return await gateway_account.sign_declare_v2_transaction(
        hello_starknet_compiled,
        compiled_class_hash=compiled_class_hash,
        max_fee=MAX_FEE,
    )


@pytest_asyncio.fixture(scope="package")
async def hello_starknet_class_hash_tx_hash(
    gateway_client: Client, declare_v2_hello_starknet: DeclareV2
) -> Tuple[int, int]:
    """
    Returns class_hash and transaction_hash from the declare_v2_hello_starknet transaction.
    """
    result = await gateway_client.declare(declare_v2_hello_starknet)
    await gateway_client.wait_for_tx(
        tx_hash=result.transaction_hash, wait_for_accept=True
    )

    return result.class_hash, result.transaction_hash


@pytest_asyncio.fixture(scope="package")
async def block_with_declare_v2_number(
    hello_starknet_class_hash_tx_hash: Tuple[int, int], full_node_client
) -> int:
    """
    Returns number of the block with DeclareV2 transaction
    """
    (_, tx_hash) = hello_starknet_class_hash_tx_hash
    declare_v2_receipt = await full_node_client.get_transaction_receipt(tx_hash)
    return declare_v2_receipt.block_number


@pytest_asyncio.fixture(scope="function")
async def replaced_class(account: Account, map_class_hash: int) -> Tuple[int, int, int]:
    """
    Returns block_number, contract_address and class_hash of transaction replacing implementation.
    """
    compiled_contract = read_contract("replace_class_compiled.json")

    declare_result = await Contract.declare(account, compiled_contract, max_fee=MAX_FEE)
    await declare_result.wait_for_acceptance()

    deploy_result = await declare_result.deploy(max_fee=MAX_FEE)
    await deploy_result.wait_for_acceptance()

    contract = deploy_result.deployed_contract

    resp = await contract.functions["replace_implementation"].invoke(
        new_class=map_class_hash, max_fee=MAX_FEE
    )
    await resp.wait_for_acceptance()

    return cast(int, resp.block_number), contract.address, map_class_hash
