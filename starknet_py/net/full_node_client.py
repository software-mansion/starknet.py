import typing
from typing import List, Optional, Union

import aiohttp
from marshmallow import EXCLUDE

from starknet_py.net.base_client import (
    BaseClient,
)
from starknet_py.net.client_models import (
    SentTransaction,
    Transaction,
    TransactionReceipt,
    BlockStateUpdate,
    StarknetBlock,
    StarknetTransaction,
    InvokeFunction,
    Hash,
    Tag,
    DeclaredContract,
    ContractClass,
)
from starknet_py.net.http_client import RpcHttpClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.rpc_schemas.rpc_schemas import (
    TransactionSchema,
    TransactionReceiptSchema,
    StarknetBlockSchema,
    BlockStateUpdateSchema,
    DeclaredContractSchema,
)
from starknet_py.net.client_utils import convert_to_felt


class FullNodeClient(BaseClient):
    def __init__(
        self,
        node_url: str,
        chain: StarknetChainId,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Client for interacting with starknet json-rpc interface.

        :param node_url: Url of the node providing rpc interface
        :param chain: Chain id of the network used by the rpc client
        :param session: Aiohttp session to be used for request. If not provided, client will create a session for
                        every request. When using a custom session, user is resposible for closing it manually.
        """
        self.url = node_url
        self._client = RpcHttpClient(url=node_url, session=session)
        self._chain = chain

    @property
    def chain(self) -> StarknetChainId:
        return self._chain

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
        raise NotImplementedError()

    async def deploy(
        self,
        contract: Union[ContractClass, str],
        constructor_calldata: List[int],
        salt: Optional[int] = None,
    ) -> SentTransaction:
        pass

    async def declare(self, contract_class: ContractClass) -> SentTransaction:
        raise NotImplementedError()

    async def get_class_hash_at(self, contract_address: Hash) -> int:
        res = await self._client.call(
            method_name="getClassHashAt",
            params={"contract_address": convert_to_felt(contract_address)},
        )
        return int(res["result"], 16)

    async def get_class_by_hash(self, class_hash: Hash) -> DeclaredContract:
        res = await self._client.call(
            method_name="getClass", params={"class_hash": convert_to_felt(class_hash)}
        )
        return DeclaredContractSchema().load(res, unknown=EXCLUDE)
