from typing import List, Optional, cast

from aiohttp import ClientSession

from starknet_py.devnet.devnet_client_models import (
    BalanceRecord,
    Config,
    Mint,
    PredeployedAccount,
)
from starknet_py.devnet.devnet_http_client import DevnetRpcHttpClient
from starknet_py.devnet.devnet_rpc_schema import (
    BalanceRecordSchema,
    ConfigSchema,
    MintSchema,
    PredeployedAccountSchema,
)
from starknet_py.net.client_models import Hash
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
class DevnetClient(FullNodeClient):
    def __init__(self, node_url: str, session: Optional[ClientSession] = None):
        super().__init__(node_url=node_url, session=session)
        self.url = node_url
        self._devnet_client = DevnetRpcHttpClient(url=node_url, session=session)

    # JSON-RPC methods

    async def mint(
        self, address: Hash, amount: int, unit: Optional[str] = None
    ) -> Mint:
        """
        Mint tokens to the given address.
        :param address: Address of the account contract.
        :param amount: Amount of tokens to mint must be integer.
        :param unit: Literals `"FRI"` or `"WEI"`, default to `"WEI"`.
        """

        res = await self._devnet_client.call(
            method_name="mint",
            params={"address": address, "amount": amount, "unit": unit},
        )

        return cast(Mint, MintSchema().load(res))

    async def get_config(self) -> Config:
        """
        Get the devnet configuration.
        """

        res = await self._devnet_client.call(method_name="getConfig")
        print(res)

        return cast(Config, ConfigSchema().load(res))

    async def get_account_balance(
        self, address: Hash, unit: Optional[str] = None, block_tag: Optional[str] = None
    ) -> BalanceRecord:
        """
        Get the balance of the given account.
        :param address: Address of the account contract.
        :param unit: Literals `"FRI"` or `"WEI"`.
        :param block_tag: Literals `"pending"` or `"latest"`.
        """

        res = await self._devnet_client.call(
            method_name="getAccountBalance",
            params={"address": address, "unit": unit, "block_tag": block_tag},
        )

        return cast(BalanceRecord, BalanceRecordSchema().load(res))

    async def get_predeployed_accounts(
        self, with_balance: Optional[bool] = None
    ) -> List[PredeployedAccount]:
        """
        Get the predeployed accounts.
        :param with_balance: If `True` the balance of the accounts will be included, default to False.
        """

        res = await self._devnet_client.call(
            method_name="getPredeployedAccounts", params={"with_balance": with_balance}
        )

        return cast(
            List[PredeployedAccount], PredeployedAccountSchema().load(res, many=True)
        )

    # REST API methods
    # async def is_alive(self) -> bool:
    #     """
    #     Check if the client is alive.
    #     """
