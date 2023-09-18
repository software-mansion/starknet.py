# pylint: disable=redefined-outer-name
from typing import Tuple, cast

import pytest
import pytest_asyncio

from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.client.fixtures.prepare_net_for_gateway_test import (
    PreparedNetworkData,
)
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V0_DIR, MAX_FEE
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
async def hello_starknet_deploy_transaction_address(
    account: Account, cairo1_hello_starknet_class_hash
) -> int:
    deployer = Deployer()
    contract_deployment = deployer.create_contract_deployment_raw(
        class_hash=cairo1_hello_starknet_class_hash
    )
    deploy_invoke_transaction = await account.sign_invoke_transaction(
        calls=contract_deployment.call, max_fee=MAX_FEE
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)
    return contract_deployment.address


@pytest_asyncio.fixture(scope="package")
async def block_with_declare_v2_number(
    cairo1_hello_starknet_tx_hash: int, client
) -> int:
    """
    Returns number of the block with DeclareV2 transaction
    """
    declare_v2_receipt = await client.get_transaction_receipt(
        cairo1_hello_starknet_tx_hash
    )
    return declare_v2_receipt.block_number


@pytest_asyncio.fixture(scope="function")
async def replaced_class(account: Account, map_class_hash: int) -> Tuple[int, int, int]:
    """
    Returns block_number, contract_address and class_hash of transaction replacing implementation.
    """
    compiled_contract = read_contract(
        "replace_class_compiled.json", directory=CONTRACTS_COMPILED_V0_DIR
    )

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
