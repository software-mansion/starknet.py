from typing import Optional, Union

import pytest

from starknet_py.net.client_models import Call, Hash, Tag
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_custom_nonce(account):
    # pylint: disable=import-outside-toplevel
    client = account.client
    address = account.address
    private_key = account.signer.key_pair.private_key

    # docs: start
    from starknet_py.net.account.account import Account
    from starknet_py.net.client import Client
    from starknet_py.net.models import AddressRepresentation, StarknetChainId
    from starknet_py.net.signer import BaseSigner
    from starknet_py.net.signer.key_pair import KeyPair

    class MyAccount(Account):
        def __init__(
            self,
            *,
            address: AddressRepresentation,
            client: Client,
            signer: Optional[BaseSigner] = None,
            key_pair: Optional[KeyPair] = None,
            chain: Optional[StarknetChainId] = None,
        ):
            super().__init__(
                address=address,
                client=client,
                signer=signer,
                key_pair=key_pair,
                chain=chain,
            )
            # Create a simple counter that will store a nonce
            self.nonce_counter = 0

        async def get_nonce(
            self,
            *,
            block_hash: Optional[Union[Hash, Tag]] = None,
            block_number: Optional[Union[int, Tag]] = None,
        ) -> int:
            # Increment the counter and return the nonce.
            # This is just an example custom nonce logic and is not meant
            # to be a recommended solution.
            nonce = self.nonce_counter
            self.nonce_counter += 1
            return nonce

    account = MyAccount(
        address=address,
        client=client,
        key_pair=KeyPair.from_private_key(private_key),
        chain=StarknetChainId.SEPOLIA,
    )
    # docs: end

    assert account.nonce_counter == 0
    await account.sign_invoke_v3(
        calls=Call(0x1, 0x1, []), resource_bounds=MAX_RESOURCE_BOUNDS
    )
    assert account.nonce_counter == 1
