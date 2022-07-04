from __future__ import annotations

from starknet_py.net import Client
from starknet_py.net.account.account_client import AccountClient
from starknet_py.net.models.chains import StarknetChainId


class DevnetClientFactory:
    def __init__(
        self,
        net: str,
        chain: StarknetChainId = StarknetChainId.TESTNET,
    ):
        self.net = net
        self.chain = chain

    async def make_devnet_client(self) -> Client:
        client = await AccountClient.create_account(net=self.net, chain=self.chain)
        return client

    async def make_devnet_client_without_account(self) -> Client:
        return Client(net=self.net, chain=self.chain)
