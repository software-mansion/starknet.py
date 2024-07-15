from typing import Tuple

import pytest

from starknet_py.devnet.devnet_client import DevnetClient
from starknet_py.net.account.account import Account
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair


@pytest.fixture(name="devnet_account", scope="package")
def devnets_account(
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
