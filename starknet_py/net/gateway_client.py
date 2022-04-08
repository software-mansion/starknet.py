from typing import Union, Optional, List

import aiohttp
from marshmallow import EXCLUDE

from starknet_py.contract import Contract
from starknet_py.net.base_client import (
    BaseClient,
    BlockHashIdentifier,
    BlockNumberIdentifier,
)
from starknet_py.net.client_models import (
    Transaction,
    SentTransaction,
    FunctionCall,
    ContractCode,
    TransactionReceipt,
    BlockState,
    StarknetBlock,
)
from starknet_py.net.gateway_schemas.gateway_schemas import (
    TransactionSchema,
    ContractCodeSchema,
    StarknetBlockSchema,
    TransactionReceiptSchema,
    FunctionCallSchema,
)


class GatewayClient(BaseClient):
    def __init__(self):
        # TODO create proper init
        feeder_gateway_url = "https://alpha4.starknet.io/feeder_gateway"
        self._g_client = GClient(url=feeder_gateway_url)

    async def get_transaction(
        self,
        tx_identifier: Union[int, BlockHashIdentifier, BlockNumberIdentifier],
    ) -> Transaction:
        if isinstance(tx_identifier, (BlockHashIdentifier, BlockNumberIdentifier)):
            raise ValueError(
                "BlockHashIdentifier and BlockNumberIdentifier are not supported in gateway client."
            )

        res = await self._g_client.call(
            method_name="get_transaction",
            params={
                "transactionHash": str(hex(tx_identifier))
                if isinstance(tx_identifier, int)
                else tx_identifier
            },
        )
        return TransactionSchema().load(res["transaction"], unknown=EXCLUDE)

    async def get_block(
        self,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> StarknetBlock:
        if block_hash is not None and block_number is not None:
            raise ValueError(
                "Block_hash and block_number parameters are mutually exclusive."
            )

        res = await self._g_client.call(
            method_name="get_block", params={"blockNumber": block_number}
        )
        return StarknetBlockSchema().load(res, unknown=EXCLUDE)

    async def get_state_update(
        self,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> BlockState:
        pass

    async def get_storage_at(
        self,
        contract_address: int,
        key: int,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> str:
        pass

    async def get_transaction_receipt(
        self, tx_hash: Union[int, str]
    ) -> TransactionReceipt:
        res = await self._g_client.call(
            method_name="get_transaction_receipt",
            params={
                "transactionHash": str(hex(tx_hash))
                if isinstance(tx_hash, int)
                else tx_hash
            },
        )
        return TransactionReceiptSchema().load(res, unknown=EXCLUDE)

    async def get_code(
        self,
        contract_address: Union[int, str],
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> ContractCode:
        block_identifier = GatewayClient._get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        params = {
            **{
                "contractAddress": str(hex(contract_address))
                if isinstance(contract_address, int)
                else contract_address
            },
            **block_identifier,
        }

        res = await self._g_client.call(method_name="get_code", params=params)
        return ContractCodeSchema().load(res, unknown=EXCLUDE)

    async def call_contract(
        self,
        invoke_tx: FunctionCall,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> List[int]:
        # TODO improve calling contracts
        block_identifier = GatewayClient._get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._g_client.post(
            method_name="call_contract",
            params=block_identifier,
            payload=FunctionCallSchema().dump(invoke_tx),
        )
        # TODO convert felts to int?
        return res["result"]

    async def add_transaction(self, tx: Transaction) -> SentTransaction:
        pass

    async def deploy(
        self,
        contract: Contract,
        constructor_calldata: List[int],
        salt: Optional[int] = None,
    ) -> SentTransaction:
        pass

    @staticmethod
    def _get_block_identifier(
        block_hash: Optional[Union[int, str]] = None, block_number: Optional[int] = None
    ) -> dict:
        if block_hash is not None and block_number is not None:
            raise ValueError(
                "Block_hash and block_number parameters are mutually exclusive."
            )

        if block_hash is not None:
            return {"blockNumber": block_number}

        if block_hash is not None:
            return {"blockNumber": block_number}

        return {}


# TODO rename
class GClient:
    def __init__(self, url):
        self.url = url

    async def call(self, method_name: str, params: dict) -> dict:
        address = f"{self.url}/{method_name}"

        # TODO add error handling
        async with aiohttp.ClientSession() as session:
            async with session.get(address, params=params) as request:
                return await request.json()

    async def post(self, method_name: str, params: dict, payload: dict) -> dict:
        address = f"{self.url}/{method_name}"

        # TODO add error handling
        async with aiohttp.ClientSession() as session:
            async with session.post(address, params=params, json=payload) as request:
                return await request.json()
