# pylint: disable=redefined-outer-name

import sys
from dataclasses import dataclass
from typing import List, Tuple

import pytest
import pytest_asyncio

from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.http_client import GatewayHttpClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.tests.e2e.fixtures.constants import (
    DEVNET_PRE_DEPLOYED_ACCOUNT_ADDRESS,
    DEVNET_PRE_DEPLOYED_ACCOUNT_PRIVATE_KEY,
    INTEGRATION_ACCOUNT_ADDRESS,
    INTEGRATION_ACCOUNT_PRIVATE_KEY,
    TESTNET_ACCOUNT_ADDRESS,
    TESTNET_ACCOUNT_PRIVATE_KEY,
)
from starknet_py.tests.e2e.utils import (
    AccountToBeDeployedDetails,
    _get_random_private_key_unsafe,
    get_deploy_account_details,
    get_deploy_account_transaction,
)


async def devnet_account_details(
    account: BaseAccount,
    class_hash: int,
) -> Tuple[str, str]:
    """
    Deploys an Account and adds fee tokens to its balance (only on devnet).
    """
    private_key = _get_random_private_key_unsafe()
    key_pair = KeyPair.from_private_key(private_key)
    salt = 1

    address = compute_address(
        class_hash=class_hash,
        constructor_calldata=[key_pair.public_key],
        salt=salt,
        deployer_address=0,
    )

    http_client = GatewayHttpClient(account.client.net)
    await http_client.post(
        method_name="mint",
        payload={
            "address": hex(address),
            "amount": int(1e30),
        },
    )

    deploy_account_tx = await get_deploy_account_transaction(
        address=address,
        key_pair=key_pair,
        salt=salt,
        class_hash=class_hash,
        network=account.client.net,
    )

    account = Account(
        address=address,
        client=account.client,
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
    )
    res = await account.client.deploy_account(deploy_account_tx)
    await account.client.wait_for_tx(res.transaction_hash)

    return hex(address), hex(key_pair.private_key)


@pytest_asyncio.fixture(scope="package")
async def address_and_private_key(
    pytestconfig,
    pre_deployed_account_with_validate_deploy: BaseAccount,
    account_with_validate_deploy_class_hash: int,
) -> Tuple[str, str]:
    """
    Returns address and private key of an account, depending on the network.
    """
    net = pytestconfig.getoption("--net")

    account_details = {
        "testnet": (TESTNET_ACCOUNT_ADDRESS, TESTNET_ACCOUNT_PRIVATE_KEY),
        "integration": (
            INTEGRATION_ACCOUNT_ADDRESS,
            INTEGRATION_ACCOUNT_PRIVATE_KEY,
        ),
    }

    if net == "devnet":
        return await devnet_account_details(
            pre_deployed_account_with_validate_deploy,
            account_with_validate_deploy_class_hash,
        )
    return account_details[net]


@pytest.fixture(scope="package")
def gateway_account(
    address_and_private_key: Tuple[str, str], gateway_client: GatewayClient
) -> BaseAccount:
    """
    Returns a new Account created with GatewayClient.
    """
    address, private_key = address_and_private_key

    return Account(
        address=address,
        client=gateway_client,
        key_pair=KeyPair.from_private_key(int(private_key, 0)),
        chain=StarknetChainId.TESTNET,
    )


@pytest.fixture(scope="package")
def full_node_account(
    address_and_private_key: Tuple[str, str], full_node_client: FullNodeClient
) -> BaseAccount:
    """
    Returns a new Account created with FullNodeClient.
    """
    address, private_key = address_and_private_key

    return Account(
        address=address,
        client=full_node_client,
        key_pair=KeyPair.from_private_key(int(private_key, 0)),
        chain=StarknetChainId.TESTNET,
    )


def net_to_base_accounts() -> List[str]:
    accounts = ["gateway_account"]
    nets = ["--net=integration", "--net=testnet", "testnet", "integration"]

    if set(nets).isdisjoint(sys.argv):
        accounts.extend(["full_node_account"])
    return accounts


@pytest.fixture(
    scope="package",
    params=net_to_base_accounts(),
)
def account(request) -> BaseAccount:
    """
    This parametrized fixture returns all new Accounts, one by one.
    """
    return request.getfixturevalue(request.param)


@dataclass
class AccountToBeDeployedDetailsFactory:

    class_hash: int
    fee_contract: Contract

    async def get(self) -> AccountToBeDeployedDetails:
        return await get_deploy_account_details(
            class_hash=self.class_hash, fee_contract=self.fee_contract
        )


@pytest_asyncio.fixture(scope="package")
async def deploy_account_details_factory(
    account_with_validate_deploy_class_hash: int,
    fee_contract: Contract,
) -> AccountToBeDeployedDetailsFactory:
    """
    Returns AccountToBeDeployedDetailsFactory.

    The Factory's get() method returns: address, key_pair, salt
    and class_hash of the account with validate deploy.
    Prefunds the address with enough tokens to allow for deployment.
    """
    return AccountToBeDeployedDetailsFactory(
        class_hash=account_with_validate_deploy_class_hash,
        fee_contract=fee_contract,
    )


@pytest.fixture(scope="package")
def pre_deployed_account_with_validate_deploy(
    pytestconfig, network: str
) -> BaseAccount:
    """
    Returns an Account pre-deployed on specified network. Used to deploy other accounts.
    """
    address_and_priv_key = {
        "devnet": (
            DEVNET_PRE_DEPLOYED_ACCOUNT_ADDRESS,
            DEVNET_PRE_DEPLOYED_ACCOUNT_PRIVATE_KEY,
        ),
        "testnet": (TESTNET_ACCOUNT_ADDRESS, TESTNET_ACCOUNT_PRIVATE_KEY),
        "integration": (
            INTEGRATION_ACCOUNT_ADDRESS,
            INTEGRATION_ACCOUNT_PRIVATE_KEY,
        ),
    }

    net = pytestconfig.getoption("--net")
    address, private_key = address_and_priv_key[net]

    return Account(
        address=address,
        client=GatewayClient(net=network),
        key_pair=KeyPair.from_private_key(int(private_key, 16)),
        chain=StarknetChainId.TESTNET,
    )
