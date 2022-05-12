from __future__ import annotations
import os


from starknet_py.net import Client
from starknet_py.net.account.account_client import AccountClient
from starknet_py.net.models.chains import StarknetChainId


DEVNET_PORT = os.environ.get("DEVNET_PORT")
if not DEVNET_PORT:
    raise RuntimeError("DEVNET_PORT environment variable not provided!")

DEVNET_ADDRESS = f"http://localhost:{DEVNET_PORT}"


class DevnetClientFactory:
    def __init__(
        self,
        net: str = DEVNET_ADDRESS,
        chain: StarknetChainId = StarknetChainId.TESTNET,
    ):
        self.net = net
        self.chain = chain

    async def make_devnet_client(self) -> Client:
        client = await AccountClient.create_account(net=self.net, chain=self.chain)
        return client

    async def make_devnet_client_without_account(self) -> Client:
        return Client(net=self.net, chain=self.chain)
