from typing import List, Optional, cast

from aiohttp import ClientSession

from starknet_py.devnet.devnet_client_models import (
    BalanceRecord,
    Config,
    IncreaseTimeResponse,
    MintResponse,
    PostmanFlushResponse,
    PredeployedAccount,
    SetTimeResponse,
)
from starknet_py.devnet.devnet_http_client import DevnetRpcHttpClient
from starknet_py.devnet.devnet_rpc_schema import (
    BalanceRecordSchema,
    ConfigSchema,
    IncreasedTimeResponseSchema,
    MintSchema,
    PostmanFlushResponseSchema,
    PredeployedAccountSchema,
    SetTimeResponseSchema,
)
from starknet_py.net.client_models import Hash, PriceUnit
from starknet_py.net.full_node_client import FullNodeClient, _to_rpc_felt
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
class DevnetClient(FullNodeClient):
    def __init__(
        self,
        node_url: str = "http://127.0.0.1:5050",
        session: Optional[ClientSession] = None,
    ):
        """
        Client for interacting with Starknet devnet json-rpc interface.

        Based on https://0xspaceshard.github.io/starknet-devnet-rs/docs/intro

        :param node_url: Url of the node providing rpc interface
        """

        super().__init__(node_url=node_url, session=session)
        self._devnet_client = DevnetRpcHttpClient(url=node_url, session=session)

    async def impersonate_account(self, address: Hash):
        """
        Impersonate the given account.
        For impersonation to work, Devnet needs to be run in forking mode.

        :param address: Address of the account contract.
        """

        await self._devnet_client.call(
            method_name="impersonateAccount",
            params={"account_address": _to_rpc_felt(address)},
        )

    async def stop_impersonate_account(self, address: Hash):
        """
        Stop impersonating the given account.

        :param address: Address of the account contract.
        """

        await self._devnet_client.call(
            method_name="stopImpersonateAccount",
            params={"account_address": _to_rpc_felt(address)},
        )

    async def auto_impersonate(self):
        """
        Enables automatic account impersonation.
        Every account that does not exist in the local state will be impersonated.
        For impersonation to work, Devnet needs to be run in forking mode.
        """

        await self._devnet_client.call(method_name="autoImpersonate")

    async def stop_auto_impersonate(self):
        await self._devnet_client.call(method_name="stopAutoImpersonate")

    async def mint(
        self, address: Hash, amount: int, unit: Optional[PriceUnit] = PriceUnit.WEI
    ) -> MintResponse:
        """
        Mint tokens to the given address.

        :param address: Address of the account contract.
        :param amount: Amount of tokens to mint. Must be integer.
        :param unit: Literals `"FRI"` or `"WEI"`, default to `"WEI"`.
        """

        unit_value = _get_unit_value(unit)

        res = await self._devnet_client.call(
            method_name="mint",
            params={
                "address": _to_rpc_felt(address),
                "amount": amount,
                "unit": unit_value,
            },
        )

        return cast(MintResponse, MintSchema().load(res))

    async def get_account_balance(
        self,
        address: Hash,
        unit: Optional[PriceUnit] = PriceUnit.WEI,
        block_tag: Optional[str] = None,
    ) -> BalanceRecord:
        """
        Get the balance of the given account.

        :param address: Address of the account contract.
        :param unit: Literals `"FRI"` or `"WEI"` defaults to `"WEI"`.
        :param block_tag: Literals `"pending"` or `"latest"`, defaults to `"latest"`.
        """

        unit_value = _get_unit_value(unit)

        res = await self._devnet_client.call(
            method_name="getAccountBalance",
            params={
                "address": _to_rpc_felt(address),
                "unit": unit_value,
                "block_tag": block_tag,
            },
        )

        return cast(BalanceRecord, BalanceRecordSchema().load(res))

    async def create_block(self) -> Hash:
        """
        Create a new block.
        """

        res = await self._devnet_client.call(method_name="createBlock")
        block_hash = res.get("block_hash")

        return cast(Hash, block_hash)

    async def abort_block(self, starting_block_hash: Hash) -> List[Hash]:
        """
        This functionality allows simulating block abortion that can occur on mainnet.
        It is supported in the --state-archive-capacity full mode.

        :param starting_block_hash: The state of Devnet will be reverted to the state before `starting_block_hash`.
        """

        res = await self._devnet_client.call(
            method_name="abortBlocks",
            params={"starting_block_hash": starting_block_hash},
        )
        aborted_block_list = res["aborted"]

        return cast(List[Hash], aborted_block_list)

    async def dump(self, path: str):
        """
        Dump the state of the devnet to a file.
        Dumping on request requires providing --dump-on mode on the startup.

        :param path: Path to the file.
        """

        await self._devnet_client.call(
            method_name="dump",
            params={"path": path},
        )

    async def load(self, path: str):
        """
        Load the state of the devnet from a file.

        :param path: Path to the file.
        """

        await self._devnet_client.call(
            method_name="load",
            params={"path": path},
        )

    async def restart(self):
        """
        Restart the devnet.
        """

        await self._devnet_client.call(
            method_name="restart",
        )

    async def postman_load(
        self, network_url: str, address: Optional[str] = None
    ) -> Hash:
        params = {"network_url": network_url}
        if address is not None:
            params["address"] = address

        res = await self._devnet_client.call(
            method_name="postmanLoad",
            params=params,
        )

        return cast(Hash, res["messaging_contract_address"])

    async def postman_flush(
        self, dry_run: Optional[bool] = False
    ) -> PostmanFlushResponse:
        res = await self._devnet_client.call(
            method_name="postmanFlush",
            params={"dry_run": dry_run},
        )
        return cast(PostmanFlushResponse, PostmanFlushResponseSchema().load(res))

    # pylint: disable=too-many-arguments
    async def send_message_to_l2(
        self,
        l2_contract_address: Hash,
        entry_point_selector: Hash,
        l1_contract_address: Hash,
        payload: List[Hash],
        nonce: Hash,
        paid_fee_on_l1: Hash,
    ) -> Hash:
        res = await self._devnet_client.call(
            method_name="postmanSendMessageToL2",
            params={
                "l2_contract_address": _to_rpc_felt(l2_contract_address),
                "entry_point_selector": _to_rpc_felt(entry_point_selector),
                "l1_contract_address": _to_rpc_felt(l1_contract_address),
                "payload": payload,
                "nonce": _to_rpc_felt(nonce),
                "paid_fee_on_l1": _to_rpc_felt(paid_fee_on_l1),
            },
        )

        return cast(Hash, res["transaction_hash"])

    async def consume_message_from_l2(
        self, from_address: Hash, to_address: Hash, payload: List[Hash]
    ) -> Hash:
        res = await self._devnet_client.call(
            method_name="postmanConsumeMessageFromL2",
            params={
                "from_address": _to_rpc_felt(from_address),
                "to_address": _to_rpc_felt(to_address),
                "payload": payload,
            },
        )

        return cast(Hash, res["message_hash"])

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

        return cast(Config, ConfigSchema().load(res))

    async def increase_time(self, time: int) -> IncreaseTimeResponse:
        """
        (Only possible if there are no pending transactions)
        Increases the block timestamp by the provided amount and generates a new block.
        All subsequent blocks will keep this increment.

        :param time: Time to increase in seconds.
        """

        res = await self._devnet_client.call(
            method_name="increaseTime", params={"time": time}
        )

        return cast(IncreaseTimeResponse, IncreasedTimeResponseSchema().load(res))

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


def _get_unit_value(unit: Optional[PriceUnit]) -> str:
    if isinstance(unit, PriceUnit):
        return cast(str, unit.value)

    return PriceUnit.WEI.value
