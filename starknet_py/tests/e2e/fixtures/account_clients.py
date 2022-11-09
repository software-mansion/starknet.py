# pylint: disable=redefined-outer-name

import sys
from dataclasses import dataclass
from typing import Tuple, List, Dict

import pytest
import pytest_asyncio
from starkware.crypto.signature.signature import get_random_private_key
from starkware.starknet.services.api.gateway.transaction import (
    DEFAULT_DECLARE_SENDER_ADDRESS,
)

from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.client import Client
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.http_client import GatewayHttpClient
from starknet_py.net.models import AddressRepresentation, StarknetChainId
from starknet_py.tests.e2e.fixtures.constants import (
    TESTNET_ACCOUNT_ADDRESS,
    TESTNET_ACCOUNT_PRIVATE_KEY,
    INTEGRATION_ACCOUNT_ADDRESS,
    INTEGRATION_ACCOUNT_PRIVATE_KEY,
    CONTRACTS_DIR,
    TESTNET_NEW_ACCOUNT_ADDRESS,
    TESTNET_NEW_ACCOUNT_PRIVATE_KEY,
    INTEGRATION_NEW_ACCOUNT_ADDRESS,
    INTEGRATION_NEW_ACCOUNT_PRIVATE_KEY,
)
from starknet_py.tests.e2e.utils import (
    AccountToBeDeployedDetails,
    get_deploy_account_details,
)
from starknet_py.transactions.deploy import make_deploy_tx


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
    network: str, gateway_client: GatewayClient
) -> Tuple[str, str]:
    """
    Creates an AccountClient (and when using devnet adds fee tokens to its balance)
    """
    devnet_account = await AccountClient.create_account(
        client=gateway_client, chain=StarknetChainId.TESTNET
    )

    http_client = GatewayHttpClient(network)
    await http_client.post(
        method_name="mint",
        payload={
            "address": hex(devnet_account.address),
            "amount": int(1e30),
        },
    )

    # Ignore typing, because BaseSigner doesn't have private_key property, but this one has
    return hex(devnet_account.address), hex(
        devnet_account.signer.private_key  # pyright: ignore
    )


@pytest_asyncio.fixture(scope="module")
async def address_and_private_key(
    pytestconfig, network: str, gateway_client: GatewayClient
) -> Tuple[str, str]:
    """
    Returns address and private key of an account, depending on the network
    """
    net = pytestconfig.getoption("--net")

    account_details = {
        "testnet": (TESTNET_ACCOUNT_ADDRESS, TESTNET_ACCOUNT_PRIVATE_KEY),
        "integration": (INTEGRATION_ACCOUNT_ADDRESS, INTEGRATION_ACCOUNT_PRIVATE_KEY),
    }

    if net == "devnet":
        return await devnet_account_details(network, gateway_client)
    return account_details[net]


@pytest.fixture(scope="module")
def gateway_account_client(
    address_and_private_key: Tuple[str, str], gateway_client: GatewayClient
) -> AccountClient:
    """
    Returns an AccountClient created with GatewayClient
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
    network: str, gateway_client: GatewayClient
) -> Tuple[str, str]:
    """
    Deploys a new AccountClient and adds fee tokens to its balance (only on devnet)
    """
    private_key = get_random_private_key()

    key_pair = KeyPair.from_private_key(private_key)
    deploy_tx = make_deploy_tx(
        constructor_calldata=[key_pair.public_key],
        compiled_contract=(CONTRACTS_DIR / "new_account_compiled.json").read_text(
            "utf-8"
        ),
    )

    result = await gateway_client.deploy(deploy_tx)
    await gateway_client.wait_for_tx(
        tx_hash=result.transaction_hash,
    )
    address = result.contract_address

    http_client = GatewayHttpClient(network)
    await http_client.post(
        method_name="mint",
        payload={
            "address": hex(address),
            "amount": int(1e30),
        },
    )

    return hex(address), hex(key_pair.private_key)


@pytest_asyncio.fixture(scope="module")
async def new_address_and_private_key(
    pytestconfig, network: str, gateway_client: GatewayClient
) -> Tuple[str, str]:
    """
    Returns address and private key of a new account, depending on the network
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
        return await new_devnet_account_details(network, gateway_client)
    return account_details[net]


@pytest.fixture(scope="module")
def new_gateway_account_client(
    new_address_and_private_key: Tuple[str, str], gateway_client: GatewayClient
) -> AccountClient:
    """
    Returns a new AccountClient created with GatewayClient
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
    Returns dict with DeclareTransaction sender_addresses depending on transaction version
    """
    return {0: DEFAULT_DECLARE_SENDER_ADDRESS, 1: new_gateway_account_client.address}
