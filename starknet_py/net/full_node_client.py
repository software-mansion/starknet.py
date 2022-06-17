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
    ContractCode,
    TransactionReceipt,
    BlockState,
    StarknetBlock,
    StarknetTransaction,
    ContractDefinition,
    InvokeFunction,
    Hash,
)
from starknet_py.net.rpc_schemas.rpc_schemas import (
    TransactionSchema,
    TransactionReceiptSchema,
    ContractCodeSchema,
    StarknetBlockSchema,
)
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_utils import convert_to_felt


class FullNodeClient(BaseClient):
    def __init__(self, node_url):
        self.url = node_url
        self.rpc_client = RpcClient(url=node_url)

    async def estimate_fee(self, tx: InvokeFunction) -> int:
        pass

    async def get_block(
        self,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> StarknetBlock:
        if block_hash is not None:
            res = await self.rpc_client.call(
                method_name="getBlockByHash",
                params={
                    "block_hash": convert_to_felt(block_hash),
                    "requested_scope": "FULL_TXNS",
                },
            )
            return StarknetBlockSchema().load(res, unknown=EXCLUDE)
        elif block_number is not None:
            res = await self.rpc_client.call(
                method_name="getBlockByNumber",
                params={"block_number": block_number, "requested_scope": "FULL_TXNS"},
            )
            return StarknetBlockSchema().load(res, unknown=EXCLUDE)
        else:
            raise ValueError("Block_hash or block_number must be provided.")

    async def get_state_update(
        self,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> BlockState:
        # TODO when pathfinder node adds support (currently untestable)
        pass

    async def get_storage_at(
        self,
        contract_address: Hash,
        key: int,
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
    ) -> int:
        if block_hash is None:
            raise ValueError("Block_hash must be provided when using FullNodeClient.")

        res = await self.rpc_client.call(
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
        res = await self.rpc_client.call(
            method_name="getTransactionByHash",
            params={"transaction_hash": convert_to_felt(tx_hash)},
        )
        return TransactionSchema().load(res, unknown=EXCLUDE)

    async def get_transaciton_by_block_hash_and_index(
        self, block_hash: Hash, index: int
    ) -> Transaction:
        res = await self.rpc_client.call(
            method_name="getTransactionByBlockHashAndIndex",
            params={
                "block_hash": convert_to_felt(block_hash),
                "index": index,
            },
        )
        return TransactionSchema().load(res, unknown=EXCLUDE)

    async def get_transaciton_by_block_number_and_index(
        self, block_number: int, index: int
    ) -> Transaction:
        res = await self.rpc_client.call(
            method_name="getTransactionByBlockNumberAndIndex",
            params={
                "block_number": block_number,
                "index": index,
            },
        )
        return TransactionSchema().load(res, unknown=EXCLUDE)

    async def get_transaction_receipt(self, tx_hash: Hash) -> TransactionReceipt:
        res = await self.rpc_client.call(
            method_name="getTransactionReceipt",
            params={"transaction_hash": convert_to_felt(tx_hash)},
        )
        return TransactionReceiptSchema().load(res, unknown=EXCLUDE)

    async def get_code(
        self,
        contract_address: Hash,
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
    ) -> ContractCode:
        res = await self.rpc_client.call(
            method_name="getCode",
            params={"contract_address": convert_to_felt(contract_address)},
        )
        return ContractCodeSchema().load(res, unknown=EXCLUDE)

    async def call_contract(
        self,
        invoke_tx: InvokeFunction,
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
    ) -> List[int]:
        if block_hash is None:
            raise ValueError("Block_hash must be provided when using FullNodeClient")

        res = await self.rpc_client.call(
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
        contract: ContractDefinition,
        constructor_calldata: List[int],
        salt: Optional[int] = None,
    ) -> SentTransaction:
        pass


class RpcClient:
    def __init__(self, url):
        self.url = url

    async def call(self, method_name: str, params: dict) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "method": f"starknet_{method_name}",
            "params": params,
            "id": 0,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload) as request:
                result = await request.json()
                if "result" not in result:
                    self.handle_full_node_exceptions(result)
                return result["result"]

    @staticmethod
    def handle_full_node_exceptions(result):
        if "error" not in result:
            raise ClientError(code="-1", message="request failed")
        raise ClientError(
            code=result["error"]["code"], message=result["error"]["message"]
        )
