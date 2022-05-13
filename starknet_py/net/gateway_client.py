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
    SentTransactionSchema,
)
from starknet_py.net.models import StarknetChainId, chain_from_network
from starknet_py.net.networks import Network, net_address_from_net
from starknet_py.net.client_errors import ClientError, ContractNotFoundError


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
        if isinstance(tx_identifier, dict):
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
        # TODO handle not received/unknown transactions
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
    ) -> int:
        block_identifier = self._get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._feeder_gateway_client.call(
            method_name="get_storage_at",
            params={
                **{
                    "contractAddress": str(hex(contract_address))
                    if isinstance(contract_address, int)
                    else contract_address,
                    "key": key,
                },
                **block_identifier,
            },
        )
        res = typing.cast(str, res)
        return int(res, 16)

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

        if len(res["bytecode"]) == 0:
            raise ContractNotFoundError(
                f"No contract found with following identifier {block_identifier}"
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
                raise TransactionRejectedError(result.transaction_rejection_reason)
            elif status == TransactionStatus.UNKNOWN:
                if not first_run:
                    raise TransactionNotReceivedError()
            elif status != TransactionStatus.RECEIVED:
                raise TransactionFailedError()

            first_run = False
            await asyncio.sleep(check_interval)

    async def estimate_fee(self, tx: InvokeFunction) -> int:
        res = await self._feeder_gateway_client.post(
            method_name="estimate_fee", payload=InvokeFunction.Schema().dump(tx)
        )
        # TODO should we have better type validation here?
        return res["amount"]

    async def call_contract(
        self,
        invoke_tx: InvokeFunction,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> List[int]:
        block_identifier = GatewayClient._get_block_identifier(
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

        # TODO gateway now supports latest block
        if block_hash == "latest":
            block_hash = "pending"

        if block_hash is not None:
            return {
                "blockHash": str(hex(block_hash))
                if isinstance(block_hash, int)
                else block_hash
            }

        if block_number is not None:
            return {"blockNumber": block_number}

        return {}


# TODO rename
class StarknetClient:
    def __init__(self, url):
        self.url = url

    async def call(self, method_name: str, params: Optional[dict] = None) -> dict:
        address = f"{self.url}/{method_name}"

        async with aiohttp.ClientSession() as session:
            async with session.get(address, params=params or {}) as request:
                if request.status != 200:
                    raise ClientError(
                        code=str(request.status), message=await request.text()
                    )
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
                    raise ClientError(
                        code=str(request.status), message=await request.text()
                    )
                return await request.json(content_type=None)
