import logging
from typing import List, Optional, cast

from aiohttp import ClientSession

from starknet_py.devnet.devnet_client_models import (
    BalanceRecord,
    Config,
    IncreasedTimeResponse,
    Mint,
    PredeployedAccount,
    SetTimeResponse,
)
from starknet_py.devnet.devnet_http_client import DevnetRpcHttpClient
from starknet_py.devnet.devnet_rpc_schema import (
    BalanceRecordSchema,
    ConfigSchema,
    IncreasedTimeResponseSchema,
    MintSchema,
    PredeployedAccountSchema,
    SetTimeResponseSchema,
)
from starknet_py.net.client_models import Hash
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
class DevnetClient(FullNodeClient):
    def __init__(self, node_url: str, session: Optional[ClientSession] = None):
        """
        Client for interacting with Starknet devnet json-rpc interface.

        Based on https://0xspaceshard.github.io/starknet-devnet-rs/docs/intro

        :param node_url: Url of the node providing rpc interface
        """

        super().__init__(node_url=node_url, session=session)
        self.url = node_url
        self._devnet_client = DevnetRpcHttpClient(url=node_url, session=session)

    async def mint(
        self, address: Hash, amount: int, unit: Optional[str] = None
    ) -> Mint:
        """
        Mint tokens to the given address.

        :param address: Address of the account contract.
        :param amount: Amount of tokens to mint. Must be integer.
        :param unit: Literals `"FRI"` or `"WEI"`, default to `"WEI"`.
        """

        res = await self._devnet_client.call(
            method_name="mint",
            params={"address": address, "amount": amount, "unit": unit},
        )

        return cast(Mint, MintSchema().load(res))

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

    async def create_block(self) -> Hash:
        """
        Create a new block.
        """

        try:
            res = await self._devnet_client.call(method_name="createBlock")
            block_hash = res.get("block_hash")
            return cast(Hash, block_hash)
        except Exception as e:
            logging.error("Failed to create block: %s", e)
            raise e

    async def abort_block(self, starting_block_hash: Hash) -> List[Hash]:
        """
        This functionality allows simulating block abortion that can occur on mainnet.
        It is supported in the --state-archive-capacity full mode.

        :param starting_block_hash: The state of Devnet will be reverted to the state before `starting_block_hash`.
        """

        try:
            res = await self._devnet_client.call(
                method_name="abortBlocks",
                params={"starting_block_hash": starting_block_hash},
            )
            aborted_block_list = res["aborted"]
            return cast(List[Hash], aborted_block_list)
        except Exception as e:
            logging.error("Failed to abort block: %s", e)
            raise e

    async def get_predeployed_accounts(
        self, with_balance: Optional[bool] = False
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

    async def get_config(self) -> Config:
        """
        Get the devnet configuration.
        """

        res = await self._devnet_client.call(method_name="getConfig")
        print(res)

        return cast(Config, ConfigSchema().load(res))

    async def increase_time(self, time: int) -> IncreasedTimeResponse:
        """
        (Only possible if there are no pending transactions)
        Increases the block timestamp by the provided amount and generates a new block.
        All subsequent blocks will keep this increment.

        :param time: Time to increase in seconds.
        """

        res = await self._devnet_client.call(
            method_name="increaseTime", params={"time": time}
        )

        return cast(IncreasedTimeResponse, IncreasedTimeResponseSchema().load(res))

    async def set_time(
        self, time: int, generate_block: Optional[bool] = False
    ) -> SetTimeResponse:
        """
        (Only possible if there are no pending transactions)
        Set the time of the devnet. Only available when there is no pending transaction.
        Warning: block time can be set in the past and lead to unexpected behaviour!

        :param time: Time to set in seconds. (Unix time)
        :param generate_block: If `True` a new block will be generated, default to False.
        """

        res = await self._devnet_client.call(
            method_name="setTime",
            params={"time": time, "generate_block": generate_block},
        )

        return cast(SetTimeResponse, SetTimeResponseSchema().load(res))
