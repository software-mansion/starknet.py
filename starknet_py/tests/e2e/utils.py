from __future__ import annotations
import os


from starknet_py.net.base_client import BaseClient
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.full_node_client import FullNodeClient
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
        net: str,
        chain: StarknetChainId = StarknetChainId.TESTNET,
    ):
        self.net = net
        self.chain = chain

    async def make_devnet_client(self) -> BaseClient:
        client = await AccountClient.create_account(net=self.net, chain=self.chain)
        return client

    async def make_devnet_client_without_account(self) -> BaseClient:
        return GatewayClient(net=self.net, chain=self.chain)

    async def make_rpc_client(self) -> BaseClient:
        return FullNodeClient(node_url=self.net + "/rpc")
