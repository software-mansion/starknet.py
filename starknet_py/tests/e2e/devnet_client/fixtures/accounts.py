import pytest_asyncio

from starknet_py.devnet_utils.devnet_client import DevnetClient
from starknet_py.net.account.account import Account
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.key_pair import KeyPair


@pytest_asyncio.fixture(scope="package")
async def account_forked_devnet(
    devnet_client_fork_mode: DevnetClient,
) -> BaseAccount:
    predeployed_account_info = (
        await devnet_client_fork_mode.get_predeployed_accounts()
    )[0]
    return Account(
        address=predeployed_account_info.address,
        client=devnet_client_fork_mode,
        key_pair=KeyPair.from_private_key(predeployed_account_info.private_key),
        chain=StarknetChainId.SEPOLIA,
    )


@pytest_asyncio.fixture(scope="package")
async def account_to_impersonate(devnet_client_fork_mode: DevnetClient) -> BaseAccount:
    """
    Creates an account instance for impersonation.

    :param address: address from Sepolia testnet that is not in the local state,
                    so it can be impersonated.
    """
    account = Account(
        address="0x043abaa073c768ebf039c0c4f46db9acc39e9ec165690418060a652aab39e7d8",
        client=devnet_client_fork_mode,
        key_pair=KeyPair(private_key="0x1", public_key="0x1"),
        chain=StarknetChainId.SEPOLIA,
    )
    await devnet_client_fork_mode.mint(account.address, int(1e40), "FRI")

    return account
