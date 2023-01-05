# pylint: disable=redefined-outer-name

import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pytest
import pytest_asyncio
from starkware.crypto.signature.signature import get_random_private_key
from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starknet.services.api.gateway.transaction import (
    DEFAULT_DECLARE_SENDER_ADDRESS,
)

from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.account._account_proxy import AccountProxy
from starknet_py.net.account.account import Account
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client import Client
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.http_client import GatewayHttpClient
from starknet_py.net.models import (
    AddressRepresentation,
    StarknetChainId,
    compute_address,
)
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import (
    DEVNET_PRE_DEPLOYED_ACCOUNT_ADDRESS,
    DEVNET_PRE_DEPLOYED_ACCOUNT_PRIVATE_KEY,
    INTEGRATION_ACCOUNT_ADDRESS,
    INTEGRATION_ACCOUNT_PRIVATE_KEY,
    INTEGRATION_NEW_ACCOUNT_ADDRESS,
    INTEGRATION_NEW_ACCOUNT_PRIVATE_KEY,
    MAX_FEE,
    TESTNET_ACCOUNT_ADDRESS,
    TESTNET_ACCOUNT_PRIVATE_KEY,
    TESTNET_NEW_ACCOUNT_ADDRESS,
    TESTNET_NEW_ACCOUNT_PRIVATE_KEY,
)
from starknet_py.tests.e2e.utils import (
    AccountToBeDeployedDetails,
    get_deploy_account_details,
    get_deploy_account_transaction,
)


def create_account_client(
    address: AddressRepresentation,
    private_key: str,
    client: Client,
    supported_tx_version: int,
) -> AccountClient:
    key_pair = KeyPair.from_private_key(int(private_key, 0))
    return AccountClient(
        address=address,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
        supported_tx_version=supported_tx_version,
    )


async def devnet_account_details(
    account: BaseAccount, class_hash: int
) -> Tuple[str, str]:
    """
    Deploys an AccountClient and adds fee tokens to its balance.
    """
    private_key = get_random_private_key()
    key_pair = KeyPair.from_private_key(private_key)

    deployer = Deployer()
    deploy_call, address = deployer.create_deployment_call_raw(
        class_hash=class_hash, raw_calldata=[key_pair.public_key]
    )

    invoke_tx = await account.sign_invoke_transaction(
        calls=deploy_call, max_fee=MAX_FEE
    )
    resp = await account.client.send_transaction(invoke_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    http_client = GatewayHttpClient(account.client.net)
    await http_client.post(
        method_name="mint",
        payload={
            "address": hex(address),
            "amount": int(1e30),
        },
    )

    return hex(address), hex(private_key)


@pytest_asyncio.fixture(scope="module")
async def address_and_private_key(
    pytestconfig,
    pre_deployed_account_with_validate_deploy: BaseAccount,
    account_without_validate_deploy_class_hash: int,
) -> Tuple[str, str]:
    """
    Returns address and private key of an account, depending on the network.
    """
    net = pytestconfig.getoption("--net")

    account_details = {
        "testnet": (TESTNET_ACCOUNT_ADDRESS, TESTNET_ACCOUNT_PRIVATE_KEY),
        "integration": (INTEGRATION_ACCOUNT_ADDRESS, INTEGRATION_ACCOUNT_PRIVATE_KEY),
    }

    if net == "devnet":
        return await devnet_account_details(
            account=pre_deployed_account_with_validate_deploy,
            class_hash=account_without_validate_deploy_class_hash,
        )
    return account_details[net]


@pytest.fixture(scope="module")
def gateway_account_client(
    address_and_private_key: Tuple[str, str], gateway_client: GatewayClient
) -> AccountClient:
    """
    Returns an AccountClient created with GatewayClient.
    """
    address, private_key = address_and_private_key

    return create_account_client(
        address, private_key, gateway_client, supported_tx_version=0
    )


@pytest.fixture(scope="module")
def full_node_account_client(
    address_and_private_key: Tuple[str, str], full_node_client: FullNodeClient
) -> AccountClient:
    """
    Returns an AccountClient created with FullNodeClient
    """
    address, private_key = address_and_private_key

    return create_account_client(
        address, private_key, full_node_client, supported_tx_version=0
    )


async def new_devnet_account_details(
    account: BaseAccount,
    class_hash: int,
) -> Tuple[str, str]:
    """
    Deploys a new AccountClient and adds fee tokens to its balance (only on devnet).
    """
    private_key = get_random_private_key()
    key_pair = KeyPair.from_private_key(private_key)
    salt = ContractAddressSalt.get_random_value()

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


@pytest_asyncio.fixture(scope="module")
async def new_address_and_private_key(
    pytestconfig,
    pre_deployed_account_with_validate_deploy: BaseAccount,
    account_with_validate_deploy_class_hash: int,
) -> Tuple[str, str]:
    """
    Returns address and private key of a new account, depending on the network.
    """
    net = pytestconfig.getoption("--net")

    account_details = {
        "testnet": (TESTNET_NEW_ACCOUNT_ADDRESS, TESTNET_NEW_ACCOUNT_PRIVATE_KEY),
        "integration": (
            INTEGRATION_NEW_ACCOUNT_ADDRESS,
            INTEGRATION_NEW_ACCOUNT_PRIVATE_KEY,
        ),
    }

    if net == "devnet":
        return await new_devnet_account_details(
            pre_deployed_account_with_validate_deploy,
            account_with_validate_deploy_class_hash,
        )
    return account_details[net]


@pytest.fixture(scope="module")
def new_gateway_account_client(
    new_address_and_private_key: Tuple[str, str], gateway_client: GatewayClient
) -> AccountClient:
    """
    Returns a new AccountClient created with GatewayClient.
    """
    address, private_key = new_address_and_private_key

    return create_account_client(
        address, private_key, gateway_client, supported_tx_version=1
    )


@pytest.fixture(scope="module")
def new_full_node_account_client(
    new_address_and_private_key: Tuple[str, str], full_node_client: FullNodeClient
) -> AccountClient:
    """
    Returns a new AccountClient created with FullNodeClient
    """
    address, private_key = new_address_and_private_key

    return create_account_client(
        address, private_key, full_node_client, supported_tx_version=1
    )


def net_to_accounts() -> List[str]:
    accounts = [
        "gateway_account_client",
        "new_gateway_account_client",
    ]
    nets = ["--net=integration", "--net=testnet", "testnet", "integration"]

    if set(nets).isdisjoint(sys.argv):
        accounts.extend(["full_node_account_client", "new_full_node_account_client"])
    return accounts


@pytest.fixture(
    scope="module",
    params=net_to_accounts(),
)
def account_client(request) -> AccountClient:
    """
    This parametrized fixture returns all AccountClients, one by one.
    """
    return request.getfixturevalue(request.param)


def net_to_new_accounts() -> List[str]:
    accounts = [
        "new_gateway_account_client",
    ]
    nets = ["--net=integration", "--net=testnet", "testnet", "integration"]

    if set(nets).isdisjoint(sys.argv):
        accounts.extend(["new_full_node_account_client"])
    return accounts


@pytest.fixture(
    scope="module",
    params=net_to_new_accounts(),
)
def new_account_client(request) -> AccountClient:
    """
    This parametrized fixture returns all new AccountClients, one by one.
    """
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="module")
def gateway_account(
    new_address_and_private_key: Tuple[str, str], gateway_client: GatewayClient
) -> BaseAccount:
    """
    Returns a new Account created with GatewayClient.
    """
    address, private_key = new_address_and_private_key

    return Account(
        address=address,
        client=gateway_client,
        key_pair=KeyPair.from_private_key(int(private_key, 0)),
        chain=StarknetChainId.TESTNET,
    )


@pytest.fixture(scope="module")
def gateway_account_proxy(new_gateway_account_client: AccountClient) -> BaseAccount:
    return AccountProxy(new_gateway_account_client)


@pytest.fixture(scope="module")
def full_node_account_proxy(new_full_node_account_client: AccountClient) -> BaseAccount:
    return AccountProxy(new_full_node_account_client)


@pytest.fixture(scope="module")
def full_node_account(
    new_address_and_private_key: Tuple[str, str], full_node_client: FullNodeClient
) -> BaseAccount:
    """
    Returns a new Account created with FullNodeClient.
    """
    address, private_key = new_address_and_private_key

    return Account(
        address=address,
        client=full_node_client,
        key_pair=KeyPair.from_private_key(int(private_key, 0)),
        chain=StarknetChainId.TESTNET,
    )


def net_to_base_accounts() -> List[str]:
    accounts = ["gateway_account", "gateway_account_proxy"]
    nets = ["--net=integration", "--net=testnet", "testnet", "integration"]

    if set(nets).isdisjoint(sys.argv):
        accounts.extend(["full_node_account", "full_node_account_proxy"])
    return accounts


@pytest.fixture(
    scope="module",
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


@pytest_asyncio.fixture(scope="module")
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


@pytest.fixture(scope="module")
def sender_address(new_gateway_account_client: AccountClient) -> Dict:
    """
    Returns dict with DeclareTransaction sender_addresses depending on transaction version.
    """
    return {0: DEFAULT_DECLARE_SENDER_ADDRESS, 1: new_gateway_account_client.address}


@pytest.fixture(scope="module")
def pre_deployed_account_with_validate_deploy(
    pytestconfig, network: str
) -> BaseAccount:
    """
    Returns an AccountClient pre-deployed on specified network. Used to deploy other accounts.
    """
    address_and_priv_key = {
        "devnet": (
            DEVNET_PRE_DEPLOYED_ACCOUNT_ADDRESS,
            DEVNET_PRE_DEPLOYED_ACCOUNT_PRIVATE_KEY,
        ),
        "testnet": (TESTNET_NEW_ACCOUNT_ADDRESS, TESTNET_NEW_ACCOUNT_PRIVATE_KEY),
        "integration": (
            INTEGRATION_NEW_ACCOUNT_ADDRESS,
            INTEGRATION_NEW_ACCOUNT_PRIVATE_KEY,
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
