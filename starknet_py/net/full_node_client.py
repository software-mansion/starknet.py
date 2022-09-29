import warnings
from typing import List, Optional, Union, cast

import aiohttp
from marshmallow import EXCLUDE

from starknet_py.net.client import (
    Client,
)
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    SentTransactionResponse,
    TransactionReceipt,
    BlockStateUpdate,
    StarknetBlock,
    InvokeFunction,
    Hash,
    Tag,
    DeclaredContract,
    Transaction,
    Declare,
    Deploy,
    EstimatedFee,
    BlockTransactionTraces,
    DeclareTransactionResponse,
    DeployTransactionResponse,
    Call,
)
from starknet_py.net.http_client import RpcHttpClient
from starknet_py.net.networks import Network
from starknet_py.net.schemas.rpc import (
    StarknetBlockSchema,
    BlockStateUpdateSchema,
    DeclaredContractSchema,
    TransactionReceiptSchema,
    TypesOfTransactionsSchema,
    SentTransactionSchema,
    DeclareTransactionResponseSchema,
    DeployTransactionResponseSchema,
    PendingTransactionsSchema,
    EstimatedFeeSchema,
)
from starknet_py.net.client_utils import convert_to_felt
from starknet_py.transaction_exceptions import TransactionNotReceivedError
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
class FullNodeClient(Client):
    def __init__(
        self,
        node_url: str,
        net: Network,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Client for interacting with starknet json-rpc interface.

        :param node_url: Url of the node providing rpc interface
        :param net: StarkNet network identifier
        :param session: Aiohttp session to be used for request. If not provided, client will create a session for
                        every request. When using a custom session, user is responsible for closing it manually.
        """
        self.url = node_url
        self._client = RpcHttpClient(url=node_url, session=session)
        self._net = net

    @property
    def net(self) -> Network:
        return self._net

    async def get_block(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> StarknetBlock:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._client.call(
            method_name="getBlockWithTxs",
            params=block_identifier,
        )
        return cast(StarknetBlock, StarknetBlockSchema().load(res, unknown=EXCLUDE))

    async def get_block_traces(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> BlockTransactionTraces:
        raise NotImplementedError()

    async def get_state_update(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> BlockStateUpdate:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._client.call(
            method_name="getStateUpdate",
            params=block_identifier,
        )
        return cast(
            BlockStateUpdate, BlockStateUpdateSchema().load(res, unknown=EXCLUDE)
        )

    async def get_storage_at(
        self,
        contract_address: Hash,
        key: int,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._client.call(
            method_name="getStorageAt",
            params={
                "contract_address": convert_to_felt(contract_address),
                "key": convert_to_felt(key),
                **block_identifier,
            },
        )
        res = cast(str, res)
        return int(res, 16)

    async def get_transaction(
        self,
        tx_hash: Hash,
    ) -> Transaction:
        try:
            res = await self._client.call(
                method_name="getTransactionByHash",
                params={"transaction_hash": convert_to_felt(tx_hash)},
            )
        except ClientError as ex:
            raise TransactionNotReceivedError() from ex
        return cast(Transaction, TypesOfTransactionsSchema().load(res, unknown=EXCLUDE))

    async def get_transaction_receipt(self, tx_hash: Hash) -> TransactionReceipt:
        res = await self._client.call(
            method_name="getTransactionReceipt",
            params={"transaction_hash": convert_to_felt(tx_hash)},
        )
        return cast(
            TransactionReceipt, TransactionReceiptSchema().load(res, unknown=EXCLUDE)
        )

    async def estimate_fee(
        self,
        tx: Union[InvokeFunction, Declare],
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> EstimatedFee:
        if isinstance(tx, Declare):
            raise ValueError(
                "Estimating fee for Declare transactions is currently not supported in FullNodeClient"
            )

        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._client.call(
            method_name="estimateFee",
            params={
                # There is no transaction_hash field in "request" since it was an error
                # in RPC v0.1.0 specification. It has been removed in the latest specification.
                "request": {
                    "max_fee": convert_to_felt(tx.max_fee),
                    "version": hex(tx.version),
                    "signature": [convert_to_felt(i) for i in tx.signature],
                    "nonce": (
                        convert_to_felt(tx.nonce) if tx.nonce is not None else None
                    ),  # TODO: verify this is correct
                    "type": "INVOKE",
                    "contract_address": convert_to_felt(tx.contract_address),
                    "entry_point_selector": convert_to_felt(tx.entry_point_selector),
                    "calldata": [convert_to_felt(i) for i in tx.calldata],
                },
                **block_identifier,
            },
        )

        return cast(EstimatedFee, EstimatedFeeSchema().load(res, unknown=EXCLUDE))

    async def call_contract(
        self,
        invoke_tx: Union[InvokeFunction, Call],
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> List[int]:
        if isinstance(invoke_tx, InvokeFunction):
            warnings.warn(
                "InvokeFunctions has been deprecated as a call_contract parameter, use Call instead.",
                category=DeprecationWarning,
            )

        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        res = await self._client.call(
            method_name="call",
            params={
                "request": _get_call_payload(invoke_tx),
                **block_identifier,
            },
        )
        return [int(i, 16) for i in res]

    async def send_transaction(
        self, transaction: InvokeFunction
    ) -> SentTransactionResponse:
        res = await self._client.call(
            method_name="addInvokeTransaction",
            params={
                "function_invocation": {
                    "contract_address": convert_to_felt(transaction.contract_address),
                    "entry_point_selector": convert_to_felt(
                        transaction.entry_point_selector
                    ),
                    "calldata": [convert_to_felt(i) for i in transaction.calldata],
                },
                "signature": [convert_to_felt(i) for i in transaction.signature],
                "max_fee": hex(transaction.max_fee),
                "version": hex(transaction.version),
            },
        )

        return cast(
            SentTransactionResponse, SentTransactionSchema().load(res, unknown=EXCLUDE)
        )

    async def deploy(self, transaction: Deploy) -> DeployTransactionResponse:
        contract_definition = transaction.dump()["contract_definition"]

        res = await self._client.call(
            method_name="addDeployTransaction",
            params={
                "contract_address_salt": convert_to_felt(
                    transaction.contract_address_salt
                ),
                "constructor_calldata": [
                    convert_to_felt(i) for i in transaction.constructor_calldata
                ],
                "contract_definition": {
                    "program": contract_definition["program"],
                    "entry_points_by_type": contract_definition["entry_points_by_type"],
                },
            },
        )

        return cast(
            DeployTransactionResponse,
            DeployTransactionResponseSchema().load(res, unknown=EXCLUDE),
        )

    async def declare(self, transaction: Declare) -> DeclareTransactionResponse:
        contract_class = transaction.dump()["contract_class"]

        res = await self._client.call(
            method_name="addDeclareTransaction",
            params={
                "contract_class": {
                    "program": contract_class["program"],
                    "entry_points_by_type": contract_class["entry_points_by_type"],
                },
                "version": hex(transaction.version),
            },
        )

        return cast(
            DeclareTransactionResponse,
            DeclareTransactionResponseSchema().load(res, unknown=EXCLUDE),
        )

    async def get_class_hash_at(
        self,
        contract_address: Hash,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        res = await self._client.call(
            method_name="getClassHashAt",
            params={
                "contract_address": convert_to_felt(contract_address),
                **block_identifier,
            },
        )
        res = cast(str, res)
        return int(res, 16)

    async def get_class_by_hash(self, class_hash: Hash) -> DeclaredContract:
        res = await self._client.call(
            method_name="getClass", params={"class_hash": convert_to_felt(class_hash)}
        )
        return cast(
            DeclaredContract, DeclaredContractSchema().load(res, unknown=EXCLUDE)
        )

    # Only RPC methods

    async def get_transaction_by_block_id(
        self,
        index: int,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> Transaction:
        """
        Get the details of transaction in block indentified block_hash and transaction index

        :param block_hash: Hash of the block
        :param index: Index of the transaction
        :return: Transaction object
        """
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._client.call(
            method_name="getTransactionByBlockIdAndIndex",
            params={
                **block_identifier,
                "index": index,
            },
        )
        return cast(Transaction, TypesOfTransactionsSchema().load(res, unknown=EXCLUDE))

    async def get_block_transaction_count(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        """
        Get the number of transactions in a block given a block id

        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: Number of transactions in the designated block
        """
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._client.call(
            method_name="getBlockTransactionCount", params=block_identifier
        )
        res = cast(int, res)
        return res

    async def get_class_at(
        self,
        contract_address: Hash,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> DeclaredContract:
        """
        Get the contract class definition in the given block at the given address

        :param contract_address: The address of the contract whose class definition will be returned
        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: Contract declared to Starknet
        """
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._client.call(
            method_name="getClassAt",
            params={
                **block_identifier,
                "contract_address": convert_to_felt(contract_address),
            },
        )

        return cast(
            DeclaredContract, DeclaredContractSchema().load(res, unknown=EXCLUDE)
        )

    async def get_pending_transactions(self) -> List[Transaction]:
        """
        Returns the transactions in the transaction pool, recognized by sequencer

        :returns: List of transactions
        """
        res = await self._client.call(method_name="pendingTransactions", params={})
        res = {"pending_transactions": res}

        return cast(
            List[Transaction], PendingTransactionsSchema().load(res, unknown=EXCLUDE)
        )

    async def get_contract_nonce(
        self,
        contract_address: int,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        res = await self._client.call(
            method_name="getNonce",
            params={
                "contract_address": convert_to_felt(contract_address),
                **block_identifier,
            },
        )
        res = cast(str, res)
        return int(res, 16)


def get_block_identifier(
    block_hash: Optional[Union[Hash, Tag]] = None,
    block_number: Optional[Union[int, Tag]] = None,
) -> dict:
    if block_hash is not None and block_number is not None:
        raise ValueError(
            "Block_hash and block_number parameters are mutually exclusive."
        )

    if block_hash in ("latest", "pending") or block_number in ("latest", "pending"):
        return {"block_id": block_hash or block_number}

    if block_hash is not None:
        return {"block_id": {"block_hash": convert_to_felt(block_hash)}}

    if block_number is not None:
        return {"block_id": {"block_number": block_number}}

    return {"block_id": "pending"}


def _get_call_payload(tx: Union[InvokeFunction, Call]) -> dict:
    if isinstance(tx, InvokeFunction):
        invoke = cast(InvokeFunction, tx)
        return {
            "contract_address": convert_to_felt(invoke.contract_address),
            "entry_point_selector": convert_to_felt(invoke.entry_point_selector),
            "calldata": [convert_to_felt(i) for i in invoke.calldata],
        }
    return {
        "contract_address": convert_to_felt(tx.to_addr),
        "entry_point_selector": convert_to_felt(tx.selector),
        "calldata": [convert_to_felt(i) for i in tx.calldata],
    }
