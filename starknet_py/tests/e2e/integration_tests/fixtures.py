import sys
from typing import List

import pytest

from starknet_py.net.account.account import Account
from starknet_py.net.client import Client
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.tests.e2e.fixtures.constants import (
    INTEGRATION_ACCOUNT_ADDRESS,
    INTEGRATION_ACCOUNT_PRIVATE_KEY,
    INTEGRATION_GATEWAY_URL,
    INTEGRATION_NODE_URL,
)


@pytest.fixture(scope="package")
def gateway_client_integration() -> GatewayClient:
    """
    A fixture returning a GatewayClient with a public integration network URL.
    """
    return GatewayClient(net=INTEGRATION_GATEWAY_URL)


@pytest.fixture(scope="package")
def full_node_client_integration() -> FullNodeClient:
    """
    A fixture returning a FullNodeClient with our integration network node URL.
    """
    return FullNodeClient(node_url=INTEGRATION_NODE_URL)


def net_to_integration_clients() -> List[str]:
    if "--client=gateway" in sys.argv:
        return ["gateway_client_integration"]
    if "--client=full_node" in sys.argv:
        return ["full_node_client_integration"]
    return ["gateway_client_integration", "full_node_client_integration"]


@pytest.fixture(
    scope="package",
    params=net_to_integration_clients(),
)
def client_integration(request) -> Client:
    """
    A fixture returning integration network clients one by one (GatewayClient, then FullNodeClient).
    """
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="package")
def gateway_account_integration(gateway_client_integration) -> Account:
    """
    A fixture returning an Account with GatewayClient.
    """
    return Account(
        address=INTEGRATION_ACCOUNT_ADDRESS,
        client=gateway_client_integration,
        key_pair=KeyPair.from_private_key(int(INTEGRATION_ACCOUNT_PRIVATE_KEY, 0)),
        chain=StarknetChainId.TESTNET,
    )


@pytest.fixture(scope="package")
def full_node_account_integration(full_node_client_integration) -> Account:
    """
    A fixture returning an Account with FullNodeClient.
    """
    return Account(
        address=INTEGRATION_ACCOUNT_ADDRESS,
        client=full_node_client_integration,
        key_pair=KeyPair.from_private_key(int(INTEGRATION_ACCOUNT_PRIVATE_KEY, 0)),
        chain=StarknetChainId.TESTNET,
    )


def net_to_integration_accounts() -> List[str]:
    if "--client=gateway" in sys.argv:
        return ["gateway_account_integration"]
    if "--client=full_node" in sys.argv:
        return ["full_node_account_integration"]
    return ["gateway_account_integration", "full_node_account_integration"]


@pytest.fixture(
    scope="package",
    params=net_to_integration_accounts(),
)
def account_integration(request) -> Account:
    """
    A fixture returning integration network accounts one by one (account with GatewayClient, then account with
    FullNodeClient).
    """
    return request.getfixturevalue(request.param)
