from typing import List

import pytest


@pytest.mark.asyncio
async def test_custom_signer():
    # pylint: disable=import-outside-toplevel, duplicate-code, unused-variable

    # docs: start
    from starknet_py.account.account import Account
    from starknet_py.client.gateway_client import GatewayClient
    from starknet_py.client.models import StarknetChainId
    from starknet_py.client.models.transaction import Transaction
    from starknet_py.client.models.typed_data import TypedData
    from starknet_py.signer import BaseSigner

    # Create a custom signer class implementing BaseSigner interface
    class CustomSigner(BaseSigner):
        @property
        def public_key(self) -> int:
            return 0x123

        def sign_transaction(self, transaction: Transaction) -> List[int]:
            return [0x0, 0x1]

        def sign_message(
            self, typed_data: TypedData, account_address: int
        ) -> List[int]:
            return [0x0, 0x1]

    # Create an Account instance with the signer you've implemented
    custom_signer = CustomSigner()
    client = GatewayClient("testnet")
    account = Account(
        client=client,
        address=0x1111,
        signer=custom_signer,
        chain=StarknetChainId.TESTNET,
    )
    # Now you can use Account as you'd always do
    # docs: end
