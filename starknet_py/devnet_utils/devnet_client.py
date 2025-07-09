import re
from typing import List, Optional, Union, cast

from aiohttp import ClientSession

from starknet_py.devnet_utils.devnet_client_models import (
    BalanceRecord,
    Config,
    IncreaseTimeResponse,
    MintResponse,
    PostmanFlushResponse,
    PredeployedAccount,
    SetTimeResponse,
)
from starknet_py.devnet_utils.devnet_rpc_schema import (
    BalanceRecordSchema,
    ConfigSchema,
    IncreasedTimeResponseSchema,
    MintResponseSchema,
    PostmanFlushResponseSchema,
    PredeployedAccountSchema,
    SetTimeResponseSchema,
)
from starknet_py.net.client_models import Hash, PriceUnit, Tag
from starknet_py.net.full_node_client import (
    FullNodeClient,
    _get_raw_block_identifier,
    _to_rpc_felt,
)
from starknet_py.net.http_client import RpcHttpClient
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
        :param session: Aiohttp session to be used for request. If not provided, client will create a session for
                        every request. When using a custom session, user is responsible for closing it manually.
        """

        super().__init__(node_url=node_url, session=session)
        self._devnet_client = RpcHttpClient(
            url=node_url, session=session, method_prefix="devnet"
        )

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
        self, address: Hash, amount: int, unit: Union[PriceUnit, str] = PriceUnit.WEI
    ) -> MintResponse:
        """
        Mint tokens to the given address.

        :param address: Address of the account contract.
        :param amount: Amount of tokens to mint. Must be integer.
        :param unit: Literals `"FRI"` or `"WEI"`, default to `"WEI"`.
        """

        res = await self._devnet_client.call(
            method_name="mint",
            params={
                "address": _to_rpc_felt(address),
                "amount": amount,
                "unit": unit.upper() if isinstance(unit, str) else unit.value,
            },
        )

        return cast(MintResponse, MintResponseSchema().load(res))

    async def get_account_balance(
        self,
        address: Hash,
        unit: Union[PriceUnit, str] = PriceUnit.WEI,
        block_tag: str = "latest",
    ) -> BalanceRecord:
        """
        Get the balance of the given account.

        :param address: Address of the account contract.
        :param unit: Literals `"FRI"` or `"WEI"` defaults to `"WEI"`.
        :param block_tag: Literals `"pre_confirmed"` or `"latest"`, defaults to `"latest"`.
        """

        res = await self._devnet_client.call(
            method_name="getAccountBalance",
            params={
                "address": _to_rpc_felt(address),
                "unit": unit.upper() if isinstance(unit, str) else unit.value,
                "block_tag": block_tag,
            },
        )

        return cast(BalanceRecord, BalanceRecordSchema().load(res))

    async def create_block(self) -> str:
        """
        Create a new block.
        """

        res = await self._devnet_client.call(method_name="createBlock")

        return res["block_hash"]

    async def abort_block(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> List[str]:
        """
        This functionality allows simulating block abortion that can occur on mainnet.
        It is supported in the `--state-archive-capacity full` mode.

        :param block_number: Number of the block which the state of Devnet will be reverted to
            or literals `"pre_confirmed"` or `"latest"`.
        :param block_hash: Hash of the block which the state of Devnet will be reverted to
            or literals `"pre_confirmed"` or `"latest"`
        """

        res = await self._devnet_client.call(
            method_name="abortBlocks",
            params={
                "starting_block_id": _get_raw_block_identifier(block_hash, block_number)
            },
        )
        return res["aborted"]

    async def dump(self, path: str):
        """
        Dump the state of the devnet to a file.
        Dumping on request requires providing `--dump-on` mode on the startup.

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
    ) -> str:
        """
        Loads a `MockStarknetMessaging
        <https://github.com/0xSpaceShard/starknet-devnet-rs/blob/138120b355c44ae60269167b326d1a267f7af0a8/contracts/l1-l2-messaging/solidity/src/MockStarknetMessaging.sol>`_
        contract. The address parameter is optional; if provided, the MockStarknetMessaging contract will be fetched
        from that address, otherwise a new one will be deployed.

        :param network_url: is the URL of the JSON-RPC API of the L1 node you've run locally or that already exists

        :return: The address of the messaging contract.
        """

        params = {"network_url": network_url}
        if address is not None:
            params["address"] = address

        res = await self._devnet_client.call(
            method_name="postmanLoad",
            params=params,
        )

        return res["messaging_contract_address"]

    async def postman_flush(self, dry_run: bool = False) -> PostmanFlushResponse:
        """
        Goes through the newly enqueued messages, sending them from L1 to L2 and from L2 to L1. Requires no body.

        :param dry_run: Optional, If `True` the result of flushing will be shown without actually triggering it.

        .. warning::
            A running L1 node is required if dry_run is not set.
        """

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
    ) -> str:
        """
        Sending mock transactions from L1 to L2 without the need for running L1.
        Deployed L2 contract address l2_contract_address and entry_point_selector must be valid
        otherwise new block will not be created. Normally nonce is calculated by L1 StarknetContract and
        it's used in L1 and L2. In this case, we need to provide it manually.

        A running L1 node is not required for this operation.

        :param l2_contract_address: Address of the L2 contract.
        :param entry_point_selector: Selector of the entry point.
        :param l1_contract_address: Address of the L1 contract.
        :param payload: List of felts.
        :param nonce: Nonce.
        :param paid_fee_on_l1: Paid fee on L1.

        :return: Transaction hash.
        """
        res = await self._devnet_client.call(
            method_name="postmanSendMessageToL2",
            params={
                "l2_contract_address": _to_rpc_felt(l2_contract_address),
                "entry_point_selector": _to_rpc_felt(entry_point_selector),
                "l1_contract_address": _to_eth_address(l1_contract_address),
                "payload": [_to_rpc_felt(entry) for entry in payload],
                "nonce": _to_rpc_felt(nonce),
                "paid_fee_on_l1": _to_rpc_felt(paid_fee_on_l1),
            },
        )

        return res["transaction_hash"]

    async def consume_message_from_l2(
        self, from_address: Hash, to_address: Hash, payload: List[Hash]
    ) -> str:
        """
        Sending mock transactions from L2 to L1. Deployed L2 contract address l2_contract_address and
        l1_contract_address must be valid.

        :param from_address: Address of the L2 contract.
        :param to_address: Address of the L1 contract.
        :param payload: List of felts.

        :return: Message hash.

        .. warning::
            A running L1 node is required for this operation.

        """
        res = await self._devnet_client.call(
            method_name="postmanConsumeMessageFromL2",
            params={
                "from_address": _to_rpc_felt(from_address),
                "to_address": _to_eth_address(to_address),
                "payload": [_to_rpc_felt(entry) for entry in payload],
            },
        )

        return res["message_hash"]

    async def get_predeployed_accounts(
        self, with_balance: bool = False
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
        Increases the block timestamp by the provided amount and generates a new block.
        All subsequent blocks will keep this increment.

        :param time: Time to increase in seconds.
        """

        res = await self._devnet_client.call(
            method_name="increaseTime", params={"time": time}
        )

        return cast(IncreaseTimeResponse, IncreasedTimeResponseSchema().load(res))

    async def set_time(
        self, time: int, generate_block: bool = False
    ) -> SetTimeResponse:
        """
        Set the time of the devnet.
        Warning: block time can be set in the past and lead to unexpected behaviour!

        :param time: Time to set in seconds. (Unix time)
        :param generate_block: If `True` a new block will be generated, default to False.
        """

        res = await self._devnet_client.call(
            method_name="setTime",
            params={"time": time, "generate_block": generate_block},
        )

        return cast(SetTimeResponse, SetTimeResponseSchema().load(res))


def _to_eth_address(value: Hash) -> str:
    """
    Convert the value to Ethereum address matching a ``^0x[a-fA-F0-9]{40}$`` pattern.

    :param value: The value to convert.
    :return: Ethereum address representation of the value.
    """
    if isinstance(value, str):
        value = int(value, 16)

    eth_address = hex(value)
    assert re.match("^0x[a-fA-F0-9]{40}$", eth_address)
    return eth_address
