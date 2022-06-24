import typing
from contextlib import nullcontext
from enum import Enum
from typing import Union, Optional, List

import aiohttp
from aiohttp import ClientSession
from marshmallow import EXCLUDE

from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starkware_utils.error_handling import StarkErrorCode


from starknet_py.net.base_client import BaseClient
from starknet_py.net.client_models import (
    Transaction,
    SentTransaction,
    ContractCode,
    TransactionReceipt,
    BlockStateUpdate,
    StarknetBlock,
    InvokeFunction,
    StarknetTransaction,
    ContractDefinition,
    Deploy,
    Hash,
    Tag,
)
from starknet_py.net.gateway_schemas.gateway_schemas import (
    TransactionSchema,
    ContractCodeSchema,
    StarknetBlockSchema,
    TransactionReceiptSchema,
    SentTransactionSchema,
    BlockStateUpdateSchema,
)
from starknet_py.net.models import StarknetChainId, chain_from_network
from starknet_py.net.networks import Network, net_address_from_net
from starknet_py.net.client_errors import ClientError, ContractNotFoundError
from starknet_py.net.client_utils import convert_to_felt, is_block_identifier
from starknet_py.transaction_exceptions import TransactionNotReceivedError


class GatewayClient(BaseClient):
    def __init__(
        self,
        net: Network,
        chain: StarknetChainId = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Client for interacting with starknet gateway.

        :param net: Target network for the client. Can be a string with URL or one of ``"mainnet"``, ``"testnet"``
        :param chain: Chain used by the network. Required if you use a custom URL for ``net`` param.
        :param session: Aiohttp session to be used for request. If not provided, client will create a session for
                        every request. When using a custom session, user is resposible for closing it manually.
        """
        host = net_address_from_net(net)
        feeder_gateway_url = f"{host}/feeder_gateway"
        gateway_url = f"{host}/gateway"

        self.chain = chain_from_network(net, chain)
        self._feeder_gateway_client = GatewayHttpClient(
            url=feeder_gateway_url, session=session
        )
        self._gateway_client = GatewayHttpClient(url=gateway_url, session=session)

    async def get_transaction(
        self,
        tx_hash: Hash,
    ) -> Transaction:
        res = await self._feeder_gateway_client.call(
            method_name="get_transaction",
            params={"transactionHash": convert_to_felt(tx_hash)},
        )

        if res["status"] in ("UNKNOWN", "NOT_RECEIVED"):
            raise TransactionNotReceivedError()

        return TransactionSchema().load(res["transaction"], unknown=EXCLUDE)

    async def get_block(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> StarknetBlock:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._feeder_gateway_client.call(
            method_name="get_block", params=block_identifier
        )
        return StarknetBlockSchema().load(res, unknown=EXCLUDE)

    async def get_state_update(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> BlockStateUpdate:
        """
        Get the information about the result of executing the requested block

        :param block_hash: Block's hash
        :param block_number: Block's number
        :return: BlockStateUpdate oject representing changes in the requested block
        """
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        res = await self._feeder_gateway_client.call(
            method_name="get_state_update",
            params=block_identifier,
        )
        return BlockStateUpdateSchema().load(res, unknown=EXCLUDE)

    async def get_storage_at(
        self,
        contract_address: Hash,
        key: int,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        """
        :param contract_address: Contract's address on Starknet
        :param key: An address of the storage variable inside the contract.
        :param block_hash: Fetches the value of the variable at given block hash
        :param block_number: See above, uses block number instead of hash
        :return: Storage value of given contract
        """
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._feeder_gateway_client.call(
            method_name="get_storage_at",
            params={
                **{
                    "contractAddress": convert_to_felt(contract_address),
                    "key": key,
                },
                **block_identifier,
            },
        )
        res = typing.cast(str, res)
        return int(res, 16)

    async def get_transaction_receipt(self, tx_hash: Hash) -> TransactionReceipt:
        res = await self._feeder_gateway_client.call(
            method_name="get_transaction_receipt",
            params={"transactionHash": convert_to_felt(tx_hash)},
        )
        return TransactionReceiptSchema().load(res, unknown=EXCLUDE)

    async def get_code(
        self,
        contract_address: Hash,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> ContractCode:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        params = {
            **{"contractAddress": convert_to_felt(contract_address)},
            **block_identifier,
        }

        res = await self._feeder_gateway_client.call(
            method_name="get_code", params=params
        )

        if len(res["bytecode"]) == 0:
            raise ContractNotFoundError(
                f"No contract found with following identifier {block_identifier}"
            )

        return ContractCodeSchema().load(res, unknown=EXCLUDE)

    async def estimate_fee(
        self,
        tx: InvokeFunction,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        res = await self._feeder_gateway_client.post(
            method_name="estimate_fee",
            payload=InvokeFunction.Schema().dump(tx),
            params=block_identifier,
        )
        # TODO should we have better type validation here?
        return res["amount"]

    async def call_contract(
        self,
        invoke_tx: InvokeFunction,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> List[int]:
        """
        Call the contract with given instance of InvokeTransaction

        :param invoke_tx: Invoke transaction
        :param block_hash: Block hash to execute the contract at specific point of time
        :param block_number: Block number (or "pending" for pending block) to execute the contract at
        :return: List of integers representing contract's function output (structured like calldata)
        """
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._feeder_gateway_client.post(
            method_name="call_contract",
            params=block_identifier,
            payload=InvokeFunction.Schema().dump(invoke_tx),
        )

        # TODO should we have better type validation here?
        return [int(v, 16) for v in res["result"]]

    async def add_transaction(self, tx: StarknetTransaction) -> SentTransaction:
        res = await self._gateway_client.post(
            method_name="add_transaction",
            payload=StarknetTransaction.Schema().dump(obj=tx),
        )
        return SentTransactionSchema().load(res, unknown=EXCLUDE)

    async def deploy(
        self,
        contract: Union[ContractDefinition, str],
        constructor_calldata: List[int],
        salt: Optional[int] = None,
    ) -> SentTransaction:
        if isinstance(contract, str):
            contract = ContractDefinition.loads(contract)

        res = await self.add_transaction(
            tx=Deploy(
                contract_address_salt=ContractAddressSalt.get_random_value()
                if salt is None
                else salt,
                contract_definition=contract,
                constructor_calldata=constructor_calldata,
                version=0,
            )
        )

        if res.code != StarkErrorCode.TRANSACTION_RECEIVED.name:
            raise TransactionNotReceivedError()

        return res


def get_block_identifier(
    block_hash: Optional[Union[Hash, Tag]] = None,
    block_number: Optional[Union[int, Tag]] = None,
) -> dict:
    if block_hash is not None and block_number is not None:
        raise ValueError(
            "Block_hash and block_number parameters are mutually exclusive."
        )

    if block_hash is not None:
        if is_block_identifier(block_hash):
            return {"block_number": block_hash}
        return {"blockHash": convert_to_felt(block_hash)}

    if block_number is not None:
        return {"blockNumber": block_number}

    return {}


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"


class GatewayHttpClient:
    def __init__(self, url, session: Optional[aiohttp.ClientSession] = None):
        self.url = url
        self.session = session

    async def gateway_request(
        self,
        http_method: HttpMethod,
        method_name: str,
        params: Optional[dict] = None,
        payload: Optional[dict] = None,
    ):
        address = f"{self.url}/{method_name}"

        async with self.http_session() as session:
            return await self._make_request(
                session=session,
                address=address,
                http_method=http_method,
                params=params or {},
                payload=payload or {},
            )

    def http_session(self) -> ClientSession:
        if self.session is not None:
            # noinspection PyTypeChecker
            return nullcontext(self.session)
        return aiohttp.ClientSession()

    @staticmethod
    async def _make_request(
        session: aiohttp.ClientSession,
        address: str,
        http_method: HttpMethod,
        params: dict,
        payload: dict,
    ) -> dict:
        async with session.request(
            method=http_method.value, url=address, params=params or {}, json=payload
        ) as request:
            if request.status != 200:
                raise ClientError(
                    code=str(request.status), message=await request.text()
                )
            return await request.json()

    async def call(self, method_name: str, params: Optional[dict] = None) -> dict:
        return await self.gateway_request(
            http_method=HttpMethod.GET, method_name=method_name, params=params
        )

    async def post(
        self, method_name: str, payload: dict, params: Optional[dict] = None
    ) -> dict:
        return await self.gateway_request(
            http_method=HttpMethod.POST,
            method_name=method_name,
            payload=payload,
            params=params,
        )
