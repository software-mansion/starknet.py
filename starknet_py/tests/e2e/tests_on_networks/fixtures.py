import pytest

from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.tests.e2e.fixtures.constants import (
    INTEGRATION_ACCOUNT_ADDRESS,
    INTEGRATION_ACCOUNT_PRIVATE_KEY,
    INTEGRATION_RPC_URL,
    TESTNET_RPC_URL,
)


@pytest.fixture(scope="package")
def full_node_client_integration() -> FullNodeClient:
    """
    A fixture returning a FullNodeClient with our integration network node URL.
    """
    # because TESTNET and INTEGRATION constants are lambdas
    return FullNodeClient(node_url=INTEGRATION_RPC_URL())


@pytest.fixture(scope="package")
def full_node_account_integration(full_node_client_integration) -> Account:
    """
    A fixture returning an Account with FullNodeClient.
    """
    return Account(
        # because TESTNET and INTEGRATION constants are lambdas
        address=INTEGRATION_ACCOUNT_ADDRESS(),
        client=full_node_client_integration,
        # because TESTNET and INTEGRATION constants are lambdas
        key_pair=KeyPair.from_private_key(int(INTEGRATION_ACCOUNT_PRIVATE_KEY(), 0)),
        chain=StarknetChainId.TESTNET,
    )


@pytest.fixture(scope="package")
def full_node_client_testnet() -> FullNodeClient:
    """
    A fixture returning a FullNodeClient with our integration network node URL.
    """
    # because TESTNET and INTEGRATION constants are lambdas
    return FullNodeClient(node_url=TESTNET_RPC_URL())
