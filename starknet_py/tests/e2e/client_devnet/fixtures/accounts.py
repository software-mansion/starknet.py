from typing import Tuple

import pytest
import pytest_asyncio

from starknet_py.devnet.devnet_client import DevnetClient
from starknet_py.net.account.account import Account
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair


@pytest.fixture(scope="package")
def account_devnet(
    address_and_private_key: Tuple[str, str], client: DevnetClient
) -> BaseAccount:
    """
    Returns a new Account created with DevnetClient.
    """
    address, private_key = address_and_private_key

    return Account(
        address=address,
        client=client,
        key_pair=KeyPair.from_private_key(int(private_key, 0)),
        chain=StarknetChainId.SEPOLIA,
    )


@pytest_asyncio.fixture(scope="package")
async def account_forked_devnet(
    devnet_forking_mode_client: DevnetClient,
) -> BaseAccount:
    predeployed_account_info = (
        await devnet_forking_mode_client.get_predeployed_accounts()
    )[0]
    return Account(
        address=predeployed_account_info.address,
        client=devnet_forking_mode_client,
        key_pair=KeyPair.from_private_key(predeployed_account_info.private_key),
        chain=StarknetChainId.SEPOLIA,
    )


@pytest.fixture(scope="package")
def account_impersonated(devnet_forking_mode_client: DevnetClient) -> BaseAccount:
    return Account(
        address="0x043abaa073c768ebf039c0c4f46db9acc39e9ec165690418060a652aab39e7d8",
        client=devnet_forking_mode_client,
        key_pair=KeyPair(private_key="0x1", public_key="0x1"),
        chain=StarknetChainId.SEPOLIA,
    )
