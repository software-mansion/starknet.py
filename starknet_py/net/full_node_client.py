import aiohttp
from typing import List, Optional, Union
from marshmallow import EXCLUDE

from starknet_py.contract import Contract
from starknet_py.net.base_client import BaseClient
from starknet_py.net.client_models import (
    SentTransaction,
    Transaction,
    FunctionCall,
    ContractCode,
    TransactionReceipt,
    BlockState,
    StarknetBlock,
)
from starknet_py.net.rpc_schemas.rpc_schemas import (
    TransactionSchema,
    TransactionReceiptSchema,
    ContractCodeSchema,
    StarknetBlockSchema,
)


class FullNodeClient(BaseClient):
    def __init__(self, url):
        self.url = url
        self.rpc_client = RpcClient(url=url)

    async def get_block(
        self,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> StarknetBlock:
        if block_hash is not None and block_number is not None:
            raise ValueError(
                "Block_hash and block_number parameters are mutually exclusive."
            )

        res = None
        if block_hash is not None:
            res = await self.rpc_client.call(
                method_name="getBlockByHash",
                params={
                    "block_hash": str(hex(block_hash)),
                    "requested_scope": "FULL_TXNS",
                },
            )
        if block_number is not None:
            res = await self.rpc_client.call(
                method_name="getBlockByNumber",
                params={"block_number": block_number, "requested_scope": "FULL_TXNS"},
            )
        return StarknetBlockSchema().load(res, unknown=EXCLUDE)

    async def get_state_update(
        self,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> BlockState:
        # TODO when pathfinder node adds support (currently untestable)
        raise NotImplementedError()

    async def get_storage_at(
        self,
        contract_address: int,
        key: int,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> str:
        res = await self.rpc_client.call(
            method_name="getStorageAt",
            params={
                "contract_address": str(hex(contract_address)),
                "key": key,
                "block_hash": str(hex(block_hash)),
            },
        )
        return res

    async def get_transaction(
        self,
        tx_hash: Union[int, str],
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
        index: Optional[int] = None,
    ) -> Transaction:
        res = await self.rpc_client.call(
            method_name="getTransactionByHash",
            params={"transaction_hash": str(hex(tx_hash))},
        )
        return TransactionSchema().load(res, unknown=EXCLUDE)

    async def get_transaction_receipt(
        self, tx_hash: Union[int, str]
    ) -> TransactionReceipt:
        res = await self.rpc_client.call(
            method_name="getTransactionReceipt",
            params={"transaction_hash": str(hex(tx_hash))},
        )
        return TransactionReceiptSchema().load(res, unknown=EXCLUDE)

    async def get_code(
        self,
        contract_address: int,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> ContractCode:
        res = await self.rpc_client.call(
            method_name="getCode",
            params={"contract_address": str(hex(contract_address))},
        )
        return ContractCodeSchema().load(res, unknown=EXCLUDE)

    async def call_contract(
        self,
        invoke_tx: FunctionCall,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> List[int]:
        raise NotImplementedError()

    async def add_transaction(self, tx: Transaction) -> SentTransaction:
        raise NotImplementedError()

    async def deploy(
        self,
        contract: Contract,
        constructor_calldata: List[int],
        salt: Optional[int] = None,
    ) -> SentTransaction:
        raise NotImplementedError()


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
                return (await request.json())["result"]
