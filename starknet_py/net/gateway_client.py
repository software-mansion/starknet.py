import typing
from typing import Union, Optional, List

import aiohttp
from marshmallow import EXCLUDE

from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starkware_utils.error_handling import StarkErrorCode


from starknet_py.net.base_client import BaseClient
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
    Hash,
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
from starknet_py.net.client_utils import convert_to_felt


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
        tx_hash: Hash,
    ) -> Transaction:
        res = await self._feeder_gateway_client.call(
            method_name="get_transaction",
            params={"transactionHash": convert_to_felt(tx_hash)},
        )
        # TODO handle not received/unknown transactions
        return TransactionSchema().load(res["transaction"], unknown=EXCLUDE)

    async def get_block(
        self,
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
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
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
    ) -> BlockState:
        # TODO implement
        pass

    async def get_storage_at(
        self,
        contract_address: Hash,
        key: int,
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
    ) -> int:
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
        print("hash " + str(tx_hash))
        res = await self._feeder_gateway_client.call(
            method_name="get_transaction_receipt",
            params={"transactionHash": convert_to_felt(tx_hash)},
        )
        print(res)
        return TransactionReceiptSchema().load(res, unknown=EXCLUDE)

    async def get_code(
        self,
        contract_address: Hash,
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
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
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
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
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
    ) -> List[int]:
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

        # TODO maybe improve/remove this exception?
        if res.code != StarkErrorCode.TRANSACTION_RECEIVED.name:
            raise Exception("Transaction not received")

        return res


def get_block_identifier(
    block_hash: Optional[Hash] = None, block_number: Optional[int] = None
) -> dict:
    if block_hash is not None and block_number is not None:
        raise ValueError(
            "Block_hash and block_number parameters are mutually exclusive."
        )

    # TODO gateway now supports latest block
    if block_hash == "latest":
        block_hash = "pending"

    if block_hash is not None:
        return {"blockHash": convert_to_felt(block_hash)}

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
