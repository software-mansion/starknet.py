import typing
import asyncio
from typing import Union, Optional, List

import aiohttp
from marshmallow import EXCLUDE

from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starkware_utils.error_handling import StarkErrorCode


from starknet_py.transaction_exceptions import (
    TransactionFailedError,
    TransactionRejectedError,
    TransactionNotReceivedError,
)
from starknet_py.net.base_client import (
    BaseClient,
    BlockHashIdentifier,
    BlockNumberIdentifier,
)
from starknet_py.net.client_models import (
    Transaction,
    SentTransaction,
    ContractCode,
    TransactionReceipt,
    BlockState,
    StarknetBlock,
    InvokeFunction,
    StarknetTransaction,
    ContractDefinition,
    Deploy,
    TransactionStatus,
)
from starknet_py.net.gateway_schemas.gateway_schemas import (
    TransactionSchema,
    ContractCodeSchema,
    StarknetBlockSchema,
    TransactionReceiptSchema,
    FunctionCallSchema,
    SentTransactionSchema,
)
from starknet_py.net.models import StarknetChainId, chain_from_network
from starknet_py.net.networks import Network, net_address_from_net


class GatewayClient(BaseClient):
    def __init__(self, net: Network, chain: StarknetChainId = None):
        host = net_address_from_net(net)
        feeder_gateway_url = f"{host}/feeder_gateway"
        gateway_url = f"{host}/gateway"

        self.chain = chain_from_network(net, chain)
        self._feeder_gateway_client = StarknetClient(url=feeder_gateway_url)
        self._gateway_client = StarknetClient(url=gateway_url)

    async def get_transaction(
        self,
        tx_identifier: Union[int, BlockHashIdentifier, BlockNumberIdentifier],
    ) -> Transaction:
        if isinstance(tx_identifier, (BlockHashIdentifier, BlockNumberIdentifier)):
            raise ValueError(
                "BlockHashIdentifier and BlockNumberIdentifier are not supported in gateway client."
            )

        res = await self._feeder_gateway_client.call(
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
        block_identifier = self._get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._feeder_gateway_client.call(
            method_name="get_block", params=block_identifier
        )
        return StarknetBlockSchema().load(res, unknown=EXCLUDE)

    async def get_state_update(
        self,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> BlockState:
        # TODO implement
        pass

    async def get_storage_at(
        self,
        contract_address: Union[int, str],
        key: int,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> str:
        block_identifier = self._get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._feeder_gateway_client.call(
            method_name="get_storage_at",
            params={
                **{
                    "contractAddress": int(hex(contract_address))
                    if isinstance(contract_address, int)
                    else contract_address,
                    "key": key,
                },
                **block_identifier,
            },
        )
        res = typing.cast(str, res)
        return str(int(res, 16))

    async def get_transaction_receipt(
        self, tx_hash: Union[int, str]
    ) -> TransactionReceipt:
        print("hash " + str(tx_hash))
        res = await self._feeder_gateway_client.call(
            method_name="get_transaction_receipt",
            params={
                "transactionHash": str(hex(tx_hash))
                if isinstance(tx_hash, int)
                else tx_hash
            },
        )
        print(res)
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

        res = await self._feeder_gateway_client.call(
            method_name="get_code", params=params
        )
        return ContractCodeSchema().load(res, unknown=EXCLUDE)

    async def wait_for_tx(
        self,
        tx_hash: Union[int, str],
        wait_for_accept: Optional[bool] = False,
        check_interval=5,
    ) -> (int, TransactionStatus):
        if check_interval <= 0:
            raise ValueError("check_interval has to bigger than 0.")

        first_run = True
        while True:
            result = await self.get_transaction_receipt(tx_hash=tx_hash)
            status = result.status

            if status in (
                TransactionStatus.ACCEPTED_ON_L1,
                TransactionStatus.ACCEPTED_ON_L2,
            ):
                return result.block_number, status
            if status == TransactionStatus.PENDING:
                if not wait_for_accept and result.block_number is not None:
                    return result.block_number, status
            elif status == TransactionStatus.REJECTED:
                # FIXME somehow get rejection message, new receipt has none due to full node format
                # raise TransactionRejectedError(str(result.transaction_failure_reason))
                raise TransactionRejectedError(result.transaction_rejection_reason)
            # FIXME new transaction status has no NOT_RECEIVED status
            elif status == TransactionStatus.UNKNOWN:
                if not first_run:
                    raise TransactionNotReceivedError()
            elif status != TransactionStatus.RECEIVED:
                raise TransactionFailedError()

            first_run = False
            await asyncio.sleep(check_interval)

    async def call_contract(
        self,
        invoke_tx: InvokeFunction,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> List[int]:
        # TODO improve calling contracts
        block_identifier = GatewayClient._get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._feeder_gateway_client.post(
            method_name="call_contract",
            params=block_identifier,
            payload=FunctionCallSchema().dump(invoke_tx),
        )
        # TODO convert felts to int?
        return res["result"]

    async def add_transaction(self, tx: StarknetTransaction) -> SentTransaction:
        res = await self._gateway_client.post(
            method_name="add_transaction",
            payload=StarknetTransaction.Schema().dump(obj=tx),
        )
        return SentTransactionSchema().load(res, unknown=EXCLUDE)

    async def deploy(
        self,
        contract: ContractDefinition,
        constructor_calldata: List[int],
        salt: Optional[int] = None,
    ) -> SentTransaction:
        # TODO remove later?
        if isinstance(contract, str):
            contract = ContractDefinition.loads(contract)

        res = await self.add_transaction(
            tx=Deploy(
                contract_address_salt=ContractAddressSalt.get_random_value()
                if salt is None
                else salt,
                contract_definition=contract,
                constructor_calldata=constructor_calldata,
            )
        )

        # TODO maybe improve/remove this exception?
        if res.code != StarkErrorCode.TRANSACTION_RECEIVED.name:
            raise Exception("Transaction not received")

        return res

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
class StarknetClient:
    def __init__(self, url):
        self.url = url

    async def call(self, method_name: str, params: Optional[dict] = None) -> dict:
        address = f"{self.url}/{method_name}"

        # TODO add error handling
        async with aiohttp.ClientSession() as session:
            async with session.get(address, params=params or {}) as request:
                if request.status != 200:
                    raise StarknetClientError(request.status, await request.text())
                return await request.json()

    async def post(
        self, method_name: str, payload: dict, params: Optional[dict] = None
    ) -> dict:
        address = f"{self.url}/{method_name}"

        # TODO add error handling
        async with aiohttp.ClientSession() as session:
            async with session.post(
                address, params=params or {}, json=payload
            ) as request:
                if request.status != 200:
                    raise StarknetClientError(request.status, await request.text())
                return await request.json(content_type=None)


class StarknetClientError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"StarknetClient request failed with code: {self.code} due to {self.message}"
