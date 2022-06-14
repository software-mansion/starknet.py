from __future__ import annotations
import os

from starknet_py.net import Client
from starknet_py.net.account.account_client import KeyPair
from starknet_py.net.account.account_client_for_tests import AccountClientForTests
from starknet_py.net.models.chains import StarknetChainId


DEVNET_PORT = os.environ.get("DEVNET_PORT")
if not DEVNET_PORT:
    raise RuntimeError("DEVNET_PORT environment variable not provided!")

DEVNET_ADDRESS = f"http://localhost:{DEVNET_PORT}"

ACCOUNT_CLIENT_ADDR = (
    "0x2109334107efc348a86e72fc3c313061c599e359d46d7b2cd48d22415585b24"
)
ACCOUNT_CLIENT_PIV_KEY = "0xcd613e30d8f16adf91b7584a2265b1f5"


class DevnetClientFactory:
    def __init__(
        self,
        net: str = DEVNET_ADDRESS,
        chain: StarknetChainId = StarknetChainId.TESTNET,
    ):
        self.net = net
        self.chain = chain

    async def make_devnet_client(self) -> Client:
        # client = await AccountClient.create_account(net=self.net, chain=self.chain)
        client = AccountClientForTests(
            ACCOUNT_CLIENT_ADDR,
            KeyPair.from_private_key(int(ACCOUNT_CLIENT_PIV_KEY, 0)),
            net=self.net,
            chain=self.chain,
        )
        return client

    async def make_devnet_client_without_account(self) -> Client:
        return Client(net=self.net, chain=self.chain)
