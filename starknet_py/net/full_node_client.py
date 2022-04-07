from typing import List, Optional, Union

import aiohttp
from marshmallow import EXCLUDE, ValidationError

from starknet_py.contract import Contract
from starknet_py.net.base_client import (
    BaseClient,
    BlockHashIdentifier,
    BlockNumberIdentifier,
)
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
from starknet_py.net.base_client_schemas import (
    BlockHashIdentifierSchema,
    BlockNumberIdentifierSchema,
)


class FullNodeClient(BaseClient):
    def __init__(self, node_url):
        self.url = node_url
        self.rpc_client = RpcClient(url=node_url)

    async def get_block(
        self,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> StarknetBlock:
        if block_hash is not None and block_number is not None:
            raise ValueError(
                "Block_hash and block_number parameters are mutually exclusive."
            )

        if block_hash is None and block_number is None:
            raise ValueError("Block_hash or block_number must be provided.")

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
        raise NotImplementedError(
            "Full node does not currently support get_state_update"
        )

    async def get_storage_at(
        self,
        contract_address: int,
        key: int,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> str:
        if block_hash is None:
            raise ValueError("Block_hash must be provided when using FullNodeClient.")

        res = await self.rpc_client.call(
            method_name="getStorageAt",
            params={
                "contract_address": str(hex(contract_address)),
                "key": str(hex(key)),
                "block_hash": str(hex(block_hash)),
            },
        )
        return res

    async def get_transaction(
        self,
        tx_identifier: Union[int, BlockHashIdentifier, BlockNumberIdentifier],
    ) -> Transaction:
        res = None
        error_message = None

        if isinstance(tx_identifier, int):
            res = await self._get_transaction_by_tx_hash(tx_identifier)

        try:
            block_hash_identifier = BlockHashIdentifierSchema().load(tx_identifier)
            res = await self._get_transaction_by_block_hash(block_hash_identifier)
        except ValidationError as ex:
            error_message = error_message or str(ex)

        try:
            block_number_identifier = BlockNumberIdentifierSchema().load(tx_identifier)
            res = await self._get_transaction_by_block_number(block_number_identifier)
        except ValidationError as ex:
            error_message = error_message or str(ex)

        if res is None:
            raise ValueError(
                f"Passed argument is not a valid tx_identifier: {error_message}"
            )

        return TransactionSchema().load(res, unknown=EXCLUDE)

    async def _get_transaction_by_tx_hash(self, tx_identifier):
        res = await self.rpc_client.call(
            method_name="getTransactionByHash",
            params={"transaction_hash": str(hex(tx_identifier))},
        )
        return res

    async def _get_transaction_by_block_hash(
        self, block_identifier: BlockHashIdentifier
    ):
        res = await self.rpc_client.call(
            method_name="getTransactionByBlockHashAndIndex",
            params={
                "block_hash": str(hex(block_identifier.block_hash)),
                "index": block_identifier.index,
            },
        )
        return res

    async def _get_transaction_by_block_number(
        self, block_identifier: BlockNumberIdentifier
    ):
        res = await self.rpc_client.call(
            method_name="getTransactionByBlockNumberAndIndex",
            params={
                "block_number": block_identifier.block_number,
                "index": block_identifier.index,
            },
        )
        return res

    async def get_transaction_receipt(
        self, tx_hash: Union[int, str]
    ) -> TransactionReceipt:
        res = await self.rpc_client.call(
            method_name="getTransactionReceipt",
            params={"transaction_hash": str(hex(tx_hash))}
            if isinstance(tx_hash, int)
            else tx_hash,
        )
        return TransactionReceiptSchema().load(res, unknown=EXCLUDE)

    async def get_code(
        self,
        contract_address: Union[int, str],
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> ContractCode:
        res = await self.rpc_client.call(
            method_name="getCode",
            params={"contract_address": str(hex(contract_address))}
            if isinstance(contract_address, int)
            else contract_address,
        )
        return ContractCodeSchema().load(res, unknown=EXCLUDE)

    async def call_contract(
        self,
        invoke_tx: FunctionCall,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> List[int]:
        if block_hash is None:
            raise ValueError("Block_hash must be provided when using FullNodeClient")

        res = await self.rpc_client.call(
            method_name="call",
            params={
                "contract_address": str(hex(invoke_tx.contract_address)),
                "entry_point_selector": str(hex(invoke_tx.entry_point_selector)),
                "calldata": [str(hex(i)) for i in invoke_tx.calldata],
                "block_hash": str(int(block_hash)),
            },
        )
        return res

    async def add_transaction(self, tx: Transaction) -> SentTransaction:
        raise NotImplementedError(
            "Full node does not currently support invoke transactions"
        )

    async def deploy(
        self,
        contract: Contract,
        constructor_calldata: List[int],
        salt: Optional[int] = None,
    ) -> SentTransaction:
        raise NotImplementedError(
            "Full node does not currently support deploy transactions"
        )


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
                    await self.handle_full_node_exceptions(result)
                return result["result"]

    @staticmethod
    def handle_full_node_exceptions(result):
        if "error" not in result:
            raise FullNodeException(code=-1, message="request failed")
        raise FullNodeException(
            code=result["error"]["code"], message=result["error"]["message"]
        )


class FullNodeException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"FullNodeClient request failed with code {self.code}: {self.message}."
