from __future__ import annotations


from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net import KeyPair
from starknet_py.net.account.account_client import AccountClient
from starknet_py.net.models.chains import StarknetChainId


ACCOUNT_CLIENT_ADDRESS = (
    "0x7d2f37b75a5e779f7da01c22acee1b66c39e8ba470ee5448f05e1462afcedb4"
)
ACCOUNT_CLIENT_PRIVATE_KEY = "0xcd613e30d8f16adf91b7584a2265b1f5"


class DevnetClientFactory:
    def __init__(
        self,
        net: str,
        chain: StarknetChainId = StarknetChainId.TESTNET,
    ):
        self.net = net
        self.chain = chain

    def make_devnet_client(self) -> AccountClient:
        key_pair = KeyPair.from_private_key(int(ACCOUNT_CLIENT_PRIVATE_KEY, 0))
        client = AccountClient(
            address=ACCOUNT_CLIENT_ADDRESS,
            client=self.make_devnet_client_without_account(),
            key_pair=key_pair,
        )

        return client

    def make_devnet_client_without_account(self) -> GatewayClient:
        return GatewayClient(net=self.net, chain=self.chain)

    def make_rpc_client(self) -> FullNodeClient:
        return FullNodeClient(
            node_url=self.net + "/rpc", chain=self.chain, net=self.net
        )
