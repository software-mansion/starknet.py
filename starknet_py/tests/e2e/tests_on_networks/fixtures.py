import pytest

from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.tests.e2e.fixtures.constants import (
    INTEGRATION_ACCOUNT_ADDRESS,
    INTEGRATION_ACCOUNT_PRIVATE_KEY,
    INTEGRATION_RPC_URL,
    TESTNET_ACCOUNT_ADDRESS,
    TESTNET_ACCOUNT_PRIVATE_KEY,
    TESTNET_RPC_URL,
)


@pytest.fixture(scope="package")
def full_node_client_integration() -> FullNodeClient:
    return FullNodeClient(node_url=INTEGRATION_RPC_URL())


@pytest.fixture(scope="package")
def full_node_account_integration(full_node_client_integration) -> Account:
    return Account(
        address=INTEGRATION_ACCOUNT_ADDRESS(),
        client=full_node_client_integration,
        key_pair=KeyPair.from_private_key(int(INTEGRATION_ACCOUNT_PRIVATE_KEY(), 0)),
        chain=StarknetChainId.TESTNET,
    )


@pytest.fixture(scope="package")
def full_node_client_testnet() -> FullNodeClient:
    return FullNodeClient(node_url=TESTNET_RPC_URL())


@pytest.fixture(scope="package")
def full_node_account_testnet(full_node_client_testnet) -> Account:
    return Account(
        address=TESTNET_ACCOUNT_ADDRESS(),
        client=full_node_client_testnet,
        key_pair=KeyPair.from_private_key(int(TESTNET_ACCOUNT_PRIVATE_KEY(), 0)),
        chain=StarknetChainId.TESTNET,
    )
