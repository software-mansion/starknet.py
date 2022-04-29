from __future__ import annotations

from starkware.crypto.signature.signature import (
    get_random_private_key,
)

from starknet_py.net import Client, KeyPair
from starknet_py.net.account.account_client import AccountClient
from starknet_py.net.account.compiled_account_contract import COMPILED_ACCOUNT_CONTRACT
from starknet_py.net.models.chains import StarknetChainId


class DevnetClient(AccountClient):
    def __init__(self, address, net, key_pair, *args, **kwargs):
        super().__init__(
            address=address,
            net=net,
            chain=StarknetChainId.TESTNET,
            key_pair=key_pair,
            *args,
            **kwargs,
        )

    @staticmethod
    async def make_devnet_client(port: int) -> DevnetClient:
        devnet_address = f"http://localhost:{port}"
        client = Client(net=devnet_address, chain="goerli")
        private_key = get_random_private_key()
        key_pair = KeyPair.from_private_key(private_key)

        result = await client.deploy(
            constructor_calldata=[key_pair.public_key],
            compiled_contract=COMPILED_ACCOUNT_CONTRACT,
        )
        await client.wait_for_tx(
            tx_hash=result["transaction_hash"],
        )
        return DevnetClient(
            address=result["address"], key_pair=key_pair, net=devnet_address
        )


class DevnetClientWithoutAccount(Client):
    def __init__(self, port):
        super().__init__(net=f"http://localhost:{port}", chain=StarknetChainId.TESTNET)
