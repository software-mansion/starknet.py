import pytest

from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.tests.e2e.fixtures.constants import (
    SEPOLIA_ACCOUNT_ADDRESS,
    SEPOLIA_ACCOUNT_PRIVATE_KEY,
    SEPOLIA_RPC_URL,
)


@pytest.fixture(scope="package")
def client_sepolia_testnet() -> FullNodeClient:
    return FullNodeClient(node_url=SEPOLIA_RPC_URL())


# pylint: disable=redefined-outer-name
@pytest.fixture(scope="package")
def account_sepolia_testnet(
    client_sepolia_testnet: FullNodeClient,
) -> Account:
    return Account(
        address=SEPOLIA_ACCOUNT_ADDRESS(),
        client=client_sepolia_testnet,
        key_pair=KeyPair.from_private_key(int(SEPOLIA_ACCOUNT_PRIVATE_KEY(), 0)),
        chain=StarknetChainId.SEPOLIA,
    )
