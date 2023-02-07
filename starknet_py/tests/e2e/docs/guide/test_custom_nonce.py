from typing import Optional

import pytest

from starknet_py.net.client_models import Call


@pytest.mark.asyncio
async def test_custom_nonce(gateway_client):
    # pylint: disable=import-outside-toplevel
    address = 0x1
    client = gateway_client
    private_key = 0x1

    # docs: start
    from starknet_py.net import KeyPair
    from starknet_py.net.account.account import Account
    from starknet_py.net.client import Client
    from starknet_py.net.models import AddressRepresentation, StarknetChainId
    from starknet_py.net.signer import BaseSigner

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

        async def get_nonce(self) -> int:
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
        chain=StarknetChainId.TESTNET,
    )
    # docs: end

    assert account.nonce_counter == 0
    await account.sign_invoke_transaction(calls=Call(0x1, 0x1, []), max_fee=10000000000)
    assert account.nonce_counter == 1
