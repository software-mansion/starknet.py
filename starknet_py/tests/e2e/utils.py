from __future__ import annotations
import os

from starknet_py.net import KeyPair
from starknet_py.net.account.account_client import AccountClient
from starkware.crypto.signature.signature import (
    get_random_private_key,
)
from starknet_py.net.account.compiled_account_contract import COMPILED_ACCOUNT_CONTRACT
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.base_client import BaseClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.full_node_client import FullNodeClient


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
    async def make_devnet_client() -> BaseClient:
        client = GatewayClient(net=DEVNET_ADDRESS, chain="goerli")
        private_key = get_random_private_key()
        key_pair = KeyPair.from_private_key(private_key)

        result = await client.deploy(
            constructor_calldata=[key_pair.public_key],
            contract=COMPILED_ACCOUNT_CONTRACT,
        )
        await client.wait_for_tx(
            tx_hash=result.hash,
        )
        return DevnetClient(address=result.address, key_pair=key_pair)


# TODO rename
class DevnetClientWithoutAccount(GatewayClient):
    def __init__(self):
        super().__init__(net=DEVNET_ADDRESS, chain=StarknetChainId.TESTNET)


# TODO rename
class DevnetClientFullNode(FullNodeClient):
    def __init__(self):
        super().__init__(node_url=f"{DEVNET_ADDRESS}/rpc")
