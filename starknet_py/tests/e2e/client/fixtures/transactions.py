# pylint: disable=redefined-outer-name
from typing import Tuple

import pytest
import pytest_asyncio

from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import DeployAccountV3
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.client.fixtures.prepare_net_for_gateway_test import (
    PreparedNetworkData,
)
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.tests.e2e.utils import (
    _get_random_private_key_unsafe,
    _new_address,
    get_deploy_account_transaction,
    prepay_account,
)


@pytest_asyncio.fixture(scope="package")
async def deploy_account_transaction(
    account_with_validate_deploy_class_hash: int,
    eth_fee_contract: Contract,
    strk_fee_contract: Contract,
    devnet,
) -> DeployAccountV3:
    """
    Returns a DeployAccount transaction
    """
    key_pair = KeyPair.from_private_key(_get_random_private_key_unsafe())

    address, salt = _new_address(
        account_with_validate_deploy_class_hash,
        [key_pair.public_key],
    )

    await prepay_account(
        address=address,
        eth_fee_contract=eth_fee_contract,
        strk_fee_contract=strk_fee_contract,
    )

    return await get_deploy_account_transaction(
        address=address,
        key_pair=key_pair,
        class_hash=account_with_validate_deploy_class_hash,
        salt=salt,
        client=FullNodeClient(devnet),
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
    account: Account, hello_starknet_class_hash
) -> int:
    deployer = Deployer()
    contract_deployment = deployer.create_contract_deployment_raw(
        class_hash=hello_starknet_class_hash
    )
    deploy_invoke_transaction = await account.sign_invoke_v3(
        calls=contract_deployment.call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)
    return contract_deployment.address


@pytest_asyncio.fixture(scope="package")
async def block_with_declare_v3_number(hello_starknet_tx_hash: int, client) -> int:
    """
    Returns number of the block with DeclareV3 transaction
    """
    declare_v3_receipt = await client.get_transaction_receipt(hello_starknet_tx_hash)
    return declare_v3_receipt.block_number
