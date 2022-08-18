import typing
import warnings
from typing import Union, Optional, List

import aiohttp
from marshmallow import EXCLUDE

from starknet_py.net.client import Client
from starknet_py.net.client_models import (
    Transaction,
    SentTransactionResponse,
    ContractCode,
    BlockStateUpdate,
    StarknetBlock,
    InvokeFunction,
    StarknetTransaction,
    Hash,
    Tag,
    DeclaredContract,
    Declare,
    Deploy,
    TransactionStatusResponse,
    EstimatedFee,
    BlockTransactionTraces,
    DeployTransactionResponse,
    DeclareTransactionResponse,
    TransactionReceipt,
)
from starknet_py.net.gateway_schemas.gateway_schemas import (
    ContractCodeSchema,
    StarknetBlockSchema,
    SentTransactionSchema,
    BlockStateUpdateSchema,
    DeclaredContractSchema,
    TypesOfTransactionsSchema,
    TransactionStatusSchema,
    BlockTransactionTracesSchema,
    EstimatedFeeSchema,
    DeployTransactionResponseSchema,
    DeclareTransactionResponseSchema,
    TransactionReceiptSchema,
)
from starknet_py.net.http_client import GatewayHttpClient
from starknet_py.net.models import StarknetChainId, chain_from_network
from starknet_py.net.networks import Network, net_address_from_net
from starknet_py.net.client_errors import ContractNotFoundError
from starknet_py.net.client_utils import convert_to_felt, is_block_identifier
from starknet_py.transaction_exceptions import TransactionNotReceivedError
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
class GatewayClient(Client):
    def __init__(
        self,
        net: Network,
        chain: Optional[StarknetChainId] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Client for interacting with starknet gateway.

        :param net: Target network for the client. Can be a string with URL, one of ``"mainnet"``, ``"testnet"``
                    or dict with ``"feeder_gateway_url"`` and ``"gateway_url"`` fields
        :param chain: Chain used by the network. Required if you use a custom URL for ``net`` param. Chain is deprecated
                        and will be removed in the next releases
        :param session: Aiohttp session to be used for request. If not provided, client will create a session for
                        every request. When using a custom session, user is resposible for closing it manually.
        """
        if isinstance(net, str):
            host = net_address_from_net(net)
            feeder_gateway_url = f"{host}/feeder_gateway"
            gateway_url = f"{host}/gateway"
        else:
            feeder_gateway_url = net["feeder_gateway_url"]
            gateway_url = net["gateway_url"]

        self._net = net

        if net in ["testnet", "mainnet"]:
            chain = chain_from_network(net, chain)
        self._chain = chain

        self._feeder_gateway_client = GatewayHttpClient(
            url=feeder_gateway_url, session=session
        )
        self._gateway_client = GatewayHttpClient(url=gateway_url, session=session)

    @property
    def chain(self) -> StarknetChainId:
        warnings.warn(
            "Chain is deprecated and will be deleted in the next releases",
            category=DeprecationWarning,
        )
        return self._chain

    @property
    def net(self) -> Network:
        return self._net

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

        return TypesOfTransactionsSchema().load(res["transaction"], unknown=EXCLUDE)

    async def get_transaction_status(
        self,
        tx_hash: Hash,
    ) -> TransactionStatusResponse:
        """
        Fetches the transaction's status and block number

        :param tx_hash: Transaction's hash representation
        :return: An object containing transaction's status and optional block hash, if transaction was accepted
        """
        res = await self._feeder_gateway_client.call(
            params={"transactionHash": convert_to_felt(tx_hash)},
            method_name="get_transaction_status",
        )
        if res["tx_status"] in ("UNKNOWN", "NOT_RECEIVED"):
            raise TransactionNotReceivedError()

        return TransactionStatusSchema().load(res)

    async def get_contract_addresses(self) -> dict:
        """
        Fetches the addresses of the StarkNet system contracts

        :return: A dictionary indexed with contract name and a value of contract's address
        """
        return await self._feeder_gateway_client.call(
            method_name="get_contract_addresses",
        )

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

    async def get_block_traces(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> BlockTransactionTraces:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._feeder_gateway_client.call(
            method_name="get_block_traces", params=block_identifier
        )
        return BlockTransactionTracesSchema().load(res, unknown=EXCLUDE)

    async def get_state_update(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> BlockStateUpdate:
        """
        Get the information about the result of executing the requested block

        :param block_hash: Block's hash
        :param block_number: Block's number (default "pending")
        :return: BlockStateUpdate object representing changes in the requested block
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
        :param block_number: See above, uses block number instead of hash (default "pending")
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
                block_hash=block_hash,
                block_number=block_identifier.get("blockNumber", None),
            )

        return ContractCodeSchema().load(res, unknown=EXCLUDE)

    async def estimate_fee(
        self,
        tx: InvokeFunction,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> EstimatedFee:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        res = await self._feeder_gateway_client.post(
            method_name="estimate_fee",
            payload=InvokeFunction.Schema().dump(tx),
            params=block_identifier,
        )

        return EstimatedFeeSchema().load(res, unknown=EXCLUDE)

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
        :param block_number: Block number (or "pending" for pending block)
            to execute the contract at (default "pending")
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

        return [int(v, 16) for v in res["result"]]

    async def send_transaction(
        self,
        transaction: InvokeFunction,
        token: Optional[str] = None,
    ) -> SentTransactionResponse:
        res = await self._add_transaction(transaction, token)
        return SentTransactionSchema().load(res, unknown=EXCLUDE)

    async def deploy(
        self,
        transaction: Deploy,
        token: Optional[str] = None,
    ) -> DeployTransactionResponse:
        res = await self._add_transaction(transaction, token)
        return DeployTransactionResponseSchema().load(res, unknown=EXCLUDE)

    async def declare(
        self,
        transaction: Declare,
        token: Optional[str] = None,
    ) -> DeclareTransactionResponse:
        res = await self._add_transaction(transaction, token)
        return DeclareTransactionResponseSchema().load(res, unknown=EXCLUDE)

    async def get_class_hash_at(self, contract_address: Hash) -> int:
        res = await self._feeder_gateway_client.call(
            method_name="get_class_hash_at",
            params={"contractAddress": convert_to_felt(contract_address)},
        )
        res = typing.cast(str, res)
        return int(res, 16)

    async def get_class_by_hash(self, class_hash: Hash) -> DeclaredContract:
        res = await self._feeder_gateway_client.call(
            method_name="get_class_by_hash",
            params={"classHash": convert_to_felt(class_hash)},
        )
        return DeclaredContractSchema().load(res, unknown=EXCLUDE)

    async def _add_transaction(
        self,
        tx: StarknetTransaction,
        token: Optional[str] = None,
    ) -> dict:
        res = await self._gateway_client.post(
            method_name="add_transaction",
            payload=StarknetTransaction.Schema().dump(obj=tx),
            params={"token": token} if token is not None else {},
        )
        return res


def get_block_identifier(
    block_hash: Optional[Union[Hash, Tag]] = None,
    block_number: Optional[Union[int, Tag]] = None,
) -> dict:
    if block_hash is not None and block_number is not None:
        raise ValueError(
            "block_hash and block_number parameters are mutually exclusive."
        )

    if block_hash is not None:
        if is_block_identifier(block_hash):
            return {"blockNumber": block_hash}
        return {"blockHash": convert_to_felt(block_hash)}

    if block_number is not None:
        return {"blockNumber": block_number}

    return {"blockNumber": "pending"}
