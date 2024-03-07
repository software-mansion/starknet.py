import pytest

from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.tests.e2e.fixtures.constants import (
    GOERLI_INTEGRATION_ACCOUNT_ADDRESS,
    GOERLI_INTEGRATION_ACCOUNT_PRIVATE_KEY,
    GOERLI_INTEGRATION_RPC_URL,
    GOERLI_TESTNET_ACCOUNT_ADDRESS,
    GOERLI_TESTNET_ACCOUNT_PRIVATE_KEY,
    GOERLI_TESTNET_RPC_URL,
    SEPOLIA_INTEGRATION_RPC_URL,
    SEPOLIA_TESTNET_RPC_URL,
)


@pytest.fixture(scope="package")
def client_goerli_integration() -> FullNodeClient:
    return FullNodeClient(node_url=GOERLI_INTEGRATION_RPC_URL())


@pytest.fixture(scope="package")
def account_goerli_integration(client_goerli_integration) -> Account:
    return Account(
        address=GOERLI_INTEGRATION_ACCOUNT_ADDRESS(),
        client=client_goerli_integration,
        key_pair=KeyPair.from_private_key(
            int(GOERLI_INTEGRATION_ACCOUNT_PRIVATE_KEY(), 0)
        ),
        chain=StarknetChainId.GOERLI,
    )


@pytest.fixture(scope="package")
def client_goerli_testnet() -> FullNodeClient:
    return FullNodeClient(node_url=GOERLI_TESTNET_RPC_URL())


@pytest.fixture(scope="package")
def account_goerli_testnet(client_goerli_testnet) -> Account:
    return Account(
        address=GOERLI_TESTNET_ACCOUNT_ADDRESS(),
        client=client_goerli_testnet,
        key_pair=KeyPair.from_private_key(int(GOERLI_TESTNET_ACCOUNT_PRIVATE_KEY(), 0)),
        chain=StarknetChainId.GOERLI,
    )


@pytest.fixture(scope="package")
def client_sepolia_integration() -> FullNodeClient:
    return FullNodeClient(node_url=SEPOLIA_INTEGRATION_RPC_URL())


@pytest.fixture(scope="package")
def client_sepolia_testnet() -> FullNodeClient:
    return FullNodeClient(node_url=SEPOLIA_TESTNET_RPC_URL())
