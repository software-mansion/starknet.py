import typing
from typing import List, Optional, Union
from contextlib import nullcontext

import aiohttp
from aiohttp import ClientSession
from marshmallow import EXCLUDE

from starknet_py.net.base_client import (
    BaseClient,
)
from starknet_py.net.client_models import (
    SentTransaction,
    Transaction,
    ContractCode,
    TransactionReceipt,
    BlockStateUpdate,
    StarknetBlock,
    StarknetTransaction,
    ContractDefinition,
    InvokeFunction,
    Hash,
    Tag,
)
from starknet_py.net.rpc_schemas.rpc_schemas import (
    TransactionSchema,
    TransactionReceiptSchema,
    ContractCodeSchema,
    StarknetBlockSchema,
    BlockStateUpdateSchema,
)
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_utils import convert_to_felt


class FullNodeClient(BaseClient):
    def __init__(self, node_url: str, session: Optional[aiohttp.ClientSession] = None):
        """
        Client for interacting with starknet json-rpc interface.

        :param node_url: Url of the node providing rpc interface
        :param session: Aiohttp session to be used for request. If not provided, client will create a session for
                        every request. When using a custom session, user is resposible for closing it manually.
        """
        self.url = node_url
        self._client = RpcHttpClient(url=node_url, session=session)

    async def get_block(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> StarknetBlock:
        if block_hash is not None:
            res = await self._client.call(
                method_name="getBlockByHash",
                params={
                    "block_hash": convert_to_felt(block_hash),
                    "requested_scope": "FULL_TXNS",
                },
            )
            return StarknetBlockSchema().load(res, unknown=EXCLUDE)
        if block_number is not None:
            res = await self._client.call(
                method_name="getBlockByNumber",
                params={"block_number": block_number, "requested_scope": "FULL_TXNS"},
            )
            return StarknetBlockSchema().load(res, unknown=EXCLUDE)
        raise ValueError("Block_hash or block_number must be provided.")

    async def get_state_update(
        self,
        block_hash: Union[Hash, Tag],
    ) -> BlockStateUpdate:
        if block_hash is None:
            raise ValueError("Block_hash must be provided when using FullNodeClient")

        res = await self._client.call(
            method_name="getStateUpdateByHash",
            params={"block_hash": convert_to_felt(block_hash)},
        )
        return BlockStateUpdateSchema().load(res, unknown=EXCLUDE)

    async def get_storage_at(
        self,
        contract_address: Hash,
        key: int,
        block_hash: Union[Hash, Tag],
    ) -> int:
        if block_hash is None:
            raise ValueError("Block_hash must be provided when using FullNodeClient")

        res = await self._client.call(
            method_name="getStorageAt",
            params={
                "contract_address": convert_to_felt(contract_address),
                "key": convert_to_felt(key),
                "block_hash": convert_to_felt(block_hash),
            },
        )
        res = typing.cast(str, res)
        return int(res, 16)

    async def get_transaction(
        self,
        tx_hash: Hash,
    ) -> Transaction:
        res = await self._client.call(
            method_name="getTransactionByHash",
            params={"transaction_hash": convert_to_felt(tx_hash)},
        )
        return TransactionSchema().load(res, unknown=EXCLUDE)

    async def get_transaction_by_block_hash(
        self, block_hash: Hash, index: int
    ) -> Transaction:
        """
        Get the details of transaction in block indentified block_hash and transaction index

        :param block_hash: Hash of the block
        :param index: Index of the transaction
        :return: Transaction object
        """
        res = await self._client.call(
            method_name="getTransactionByBlockHashAndIndex",
            params={
                "block_hash": convert_to_felt(block_hash),
                "index": index,
            },
        )
        return TransactionSchema().load(res, unknown=EXCLUDE)

    async def get_transaction_by_block_number(
        self, block_number: int, index: int
    ) -> Transaction:
        """
        Get the details of transaction in block indentified block number and transaction index

        :param block_number: Number of the block
        :param index: Index of the transaction
        :return: Transaction object
        """
        res = await self._client.call(
            method_name="getTransactionByBlockNumberAndIndex",
            params={
                "block_number": block_number,
                "index": index,
            },
        )
        return TransactionSchema().load(res, unknown=EXCLUDE)

    async def get_transaction_receipt(self, tx_hash: Hash) -> TransactionReceipt:
        res = await self._client.call(
            method_name="getTransactionReceipt",
            params={"transaction_hash": convert_to_felt(tx_hash)},
        )
        return TransactionReceiptSchema().load(res, unknown=EXCLUDE)

    async def get_code(
        self,
        contract_address: Hash,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> ContractCode:
        res = await self._client.call(
            method_name="getCode",
            params={"contract_address": convert_to_felt(contract_address)},
        )
        return ContractCodeSchema().load(res, unknown=EXCLUDE)

    async def estimate_fee(
        self,
        tx: InvokeFunction,
        block_hash: Union[Hash, Tag] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        pass

    async def call_contract(
        self, invoke_tx: InvokeFunction, block_hash: Union[Hash, Tag] = None
    ) -> List[int]:

        if block_hash is None:
            raise ValueError("Block_hash must be provided when using FullNodeClient")

        res = await self._client.call(
            method_name="call",
            params={
                "contract_address": convert_to_felt(invoke_tx.contract_address),
                "entry_point_selector": convert_to_felt(invoke_tx.entry_point_selector),
                "calldata": [convert_to_felt(i) for i in invoke_tx.calldata],
                "block_hash": convert_to_felt(block_hash),
            },
        )
        return [int(i, 16) for i in res["result"]]

    async def add_transaction(self, tx: StarknetTransaction) -> SentTransaction:
        pass

    async def deploy(
        self,
        contract: Union[ContractDefinition, str],
        constructor_calldata: List[int],
        salt: Optional[int] = None,
    ) -> SentTransaction:
        pass


class RpcHttpClient:
    def __init__(self, url, session: Optional[aiohttp.ClientSession] = None):
        self.url = url
        self.session = session

    async def call(self, method_name: str, params: dict) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "method": f"starknet_{method_name}",
            "params": params,
            "id": 0,
        }

        async with self.http_session() as session:
            return await self._make_request(session=session, payload=payload)

    def http_session(self) -> ClientSession:
        if self.session is not None:
            # noinspection PyTypeChecker
            return nullcontext(self.session)
        return aiohttp.ClientSession()

    async def _make_request(
        self, session: aiohttp.ClientSession, payload: dict
    ) -> dict:
        async with session.post(self.url, json=payload) as request:
            result = await request.json()
            if "result" not in result:
                self.handle_error(result)
            return result["result"]

    @staticmethod
    def handle_error(result):
        if "error" not in result:
            raise ClientError(code="-1", message="request failed")
        raise ClientError(
            code=result["error"]["code"], message=result["error"]["message"]
        )
