from __future__ import annotations
import os

from starkware.crypto.signature.signature import (
    get_random_private_key,
)

from starknet_py.net import Client, KeyPair
from starknet_py.net.account.account_client import AccountClient
from starknet_py.net.account.compiled_account_contract import COMPILED_ACCOUNT_CONTRACT
from starknet_py.net.models.chains import StarknetChainId


DEVNET_PORT = os.environ.get("DEVNET_PORT")
if not DEVNET_PORT:
    raise RuntimeError("DEVNET_PORT environment variable not provided!")

DEVNET_ADDRESS = f"http://localhost:{DEVNET_PORT}"


class DevnetClient(AccountClient):
    def __init__(self, address, key_pair, *args, **kwargs):
        super().__init__(
            address=address,
            net=DEVNET_ADDRESS,
            chain=StarknetChainId.TESTNET,
            key_pair=key_pair,
            *args,
            **kwargs,
        )

    @staticmethod
    async def make_devnet_client() -> DevnetClient:
        # pylint: disable=duplicate-code

        client = Client(net=DEVNET_ADDRESS, chain="goerli")
        private_key = get_random_private_key()
        key_pair = KeyPair.from_private_key(private_key)

        result = await client.deploy(
            constructor_calldata=[key_pair.public_key],
            compiled_contract=COMPILED_ACCOUNT_CONTRACT,
        )
        await client.wait_for_tx(
            tx_hash=result["transaction_hash"],
        )
        return DevnetClient(address=result["address"], key_pair=key_pair)


class DevnetClientWithoutAccount(Client):
    def __init__(self):
        super().__init__(net=DEVNET_ADDRESS, chain=StarknetChainId.TESTNET)
