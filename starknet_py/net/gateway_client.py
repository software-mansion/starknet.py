import warnings
from typing import Dict, List, Optional, Union, cast

import aiohttp
from marshmallow import EXCLUDE

from starknet_py.net.client import Client
from starknet_py.net.client_errors import ContractNotFoundError
from starknet_py.net.client_models import (
    BlockStateUpdate,
    BlockTransactionTraces,
    Call,
    CasmClass,
    ContractClass,
    ContractCode,
    DeclareTransactionResponse,
    DeployAccountTransactionResponse,
    EstimatedFee,
    GatewayBlock,
    GatewayTransactionStatusResponse,
    Hash,
    SentTransactionResponse,
    SierraContractClass,
    SignatureOnStateDiff,
    StateUpdateWithBlock,
    Tag,
    Transaction,
    TransactionReceipt,
)
from starknet_py.net.client_utils import hash_to_felt, is_block_identifier
from starknet_py.net.http_client import GatewayHttpClient
from starknet_py.net.models.transaction import (
    AccountTransaction,
    Declare,
    DeclareSchema,
    DeclareV2,
    DeclareV2Schema,
    DeployAccount,
    DeployAccountSchema,
    Invoke,
    InvokeSchema,
    compress_program,
)
from starknet_py.net.networks import Network, net_address_from_net
from starknet_py.net.schemas.gateway import (
    BlockStateUpdateSchema,
    BlockTransactionTracesSchema,
    CasmClassSchema,
    ContractCodeSchema,
    DeclareTransactionResponseSchema,
    DeployAccountTransactionResponseSchema,
    EstimatedFeeSchema,
    SentTransactionSchema,
    SignatureOnStateDiffSchema,
    StarknetBlockSchema,
    StateUpdateWithBlockSchema,
    TransactionReceiptSchema,
    TransactionStatusSchema,
    TypesOfContractClassSchema,
    TypesOfTransactionsSchema,
)
from starknet_py.transaction_errors import TransactionNotReceivedError
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
class GatewayClient(Client):
    # pylint: disable=too-many-public-methods
    def __init__(
        self,
        net: Network,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        .. deprecated:: 0.17.0
            Gateway / Feeder Gateway API will become deprecated in the future. As a result, GatewayClient won't work
            and will eventually be removed. Consider migrating to FullNodeClient.


        Client for interacting with Starknet gateway.

        :param net: Target network for the client. Can be a string with URL, one of ``"mainnet"``, ``"testnet"``
                    or dict with ``"feeder_gateway_url"`` and ``"gateway_url"`` fields
        :param session: Aiohttp session to be used for request. If not provided, client will create a session for
                        every request. When using a custom session, user is responsible for closing it manually.
        """
        warnings.warn(
            "Gateway / Feeder Gateway API will become deprecated in the future. As a result, GatewayClient won't work "
            "and will eventually be removed. Consider migrating to FullNodeClient.",
            PendingDeprecationWarning,
        )

        if isinstance(net, str):
            host = net_address_from_net(net)
            feeder_gateway_url = f"{host}/feeder_gateway"
            gateway_url = f"{host}/gateway"
        else:
            feeder_gateway_url = net["feeder_gateway_url"]
            gateway_url = net["gateway_url"]

        self._net = net

        self._feeder_gateway_client = GatewayHttpClient(
            url=feeder_gateway_url, session=session
        )
        self._gateway_client = GatewayHttpClient(url=gateway_url, session=session)

    @property
    def net(self) -> Network:
        warnings.warn(
            "Property net is deprecated in the GatewayClient.",
            category=DeprecationWarning,
        )
        return self._net

    async def get_block(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> GatewayBlock:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._feeder_gateway_client.call(
            method_name="get_block", params=block_identifier
        )
        return StarknetBlockSchema().load(res, unknown=EXCLUDE)  # pyright: ignore

    async def trace_block_transactions(
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
        return BlockTransactionTracesSchema().load(
            res, unknown=EXCLUDE
        )  # pyright: ignore

    async def get_state_update(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
        include_block: bool = False,
    ) -> Union[BlockStateUpdate, StateUpdateWithBlock]:
        """
        Get the information about the result of executing the requested block.

        :param block_hash: Block's hash.
        :param block_number: Block's number (default "pending").
        :param include_block: Flag deciding whether to include the queried block. Defaults to false.
        :return: BlockStateUpdate object representing changes in the requested block.
        """
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        params = {
            **block_identifier,
            "includeBlock": str(include_block).lower(),
        }
        res = await self._feeder_gateway_client.call(
            method_name="get_state_update", params=params
        )

        if include_block:
            return StateUpdateWithBlockSchema().load(
                res, unknown=EXCLUDE
            )  # pyright: ignore
        return BlockStateUpdateSchema().load(res, unknown=EXCLUDE)  # pyright: ignore

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
                    "contractAddress": hash_to_felt(contract_address),
                    "key": key,
                },
                **block_identifier,
            },
        )
        res = cast(str, res)
        return int(res, 16)

    async def get_transaction(
        self,
        tx_hash: Hash,
    ) -> Transaction:
        res = await self._feeder_gateway_client.call(
            method_name="get_transaction",
            params={"transactionHash": hash_to_felt(tx_hash)},
        )

        if res["status"] in ("UNKNOWN", "NOT_RECEIVED"):
            raise TransactionNotReceivedError()

        return cast(
            Transaction,
            TypesOfTransactionsSchema().load(res["transaction"], unknown=EXCLUDE),
        )

    async def get_transaction_receipt(self, tx_hash: Hash) -> TransactionReceipt:
        res = await self._feeder_gateway_client.call(
            method_name="get_transaction_receipt",
            params={"transactionHash": hash_to_felt(tx_hash)},
        )

        return TransactionReceiptSchema().load(res, unknown=EXCLUDE)  # pyright: ignore

    async def estimate_fee(
        self,
        tx: Union[AccountTransaction, List[AccountTransaction]],
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> Union[EstimatedFee, List[EstimatedFee]]:
        if isinstance(tx, list):
            return await self.estimate_fee_bulk(
                transactions=tx, block_hash=block_hash, block_number=block_number
            )

        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        res = await self._feeder_gateway_client.post(
            method_name="estimate_fee",
            payload=_get_payload(tx),
            params=block_identifier,
        )

        return EstimatedFeeSchema().load(res, unknown=EXCLUDE)  # pyright: ignore

    async def estimate_fee_bulk(
        self,
        transactions: List[AccountTransaction],
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> List[EstimatedFee]:
        """
        Estimate how much Wei it will cost to run provided transactions.

        :param transactions: List of transactions to estimate.
        :param block_hash: Block's hash or literals `"pending"` or `"latest"`.
        :param block_number: Block's number or literals `"pending"` or `"latest"`.
        :return: List of estimated amount of Wei executing specified transaction will cost.
        """

        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        res = await self._feeder_gateway_client.post(
            method_name="estimate_fee_bulk",
            payload=_get_payload(transactions),
            params=block_identifier,
        )

        return EstimatedFeeSchema().load(
            res, unknown=EXCLUDE, many=True
        )  # pyright: ignore

    async def call_contract(
        self,
        call: Call,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> List[int]:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )

        res = await self._feeder_gateway_client.post(
            method_name="call_contract",
            params=block_identifier,
            payload={
                "contract_address": hex(call.to_addr),
                "entry_point_selector": hex(call.selector),
                "calldata": [str(i) for i in call.calldata],
            },
        )

        return [int(v, 16) for v in res["result"]]

    async def send_transaction(
        self,
        transaction: Invoke,
        token: Optional[str] = None,
    ) -> SentTransactionResponse:
        res = await self._add_transaction(transaction, token)
        return SentTransactionSchema().load(res, unknown=EXCLUDE)  # pyright: ignore

    async def deploy_account(
        self, transaction: DeployAccount, token: Optional[str] = None
    ) -> DeployAccountTransactionResponse:
        res = await self._add_transaction(transaction, token)
        return DeployAccountTransactionResponseSchema().load(
            res, unknown=EXCLUDE
        )  # pyright: ignore

    async def declare(
        self,
        transaction: Union[Declare, DeclareV2],
        token: Optional[str] = None,
    ) -> DeclareTransactionResponse:
        res = await self._add_transaction(transaction, token)
        return DeclareTransactionResponseSchema().load(
            res, unknown=EXCLUDE
        )  # pyright: ignore

    async def get_class_hash_at(
        self,
        contract_address: Hash,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        res = await self._feeder_gateway_client.call(
            method_name="get_class_hash_at",
            params={
                "contractAddress": hash_to_felt(contract_address),
                **block_identifier,
            },
        )
        res = cast(str, res)
        return int(res, 16)

    async def get_class_by_hash(
        self, class_hash: Hash
    ) -> Union[ContractClass, SierraContractClass]:
        res = await self._feeder_gateway_client.call(
            method_name="get_class_by_hash",
            params={"classHash": hash_to_felt(class_hash)},
        )
        return TypesOfContractClassSchema().load(
            res, unknown=EXCLUDE
        )  # pyright: ignore

    # Only gateway methods

    async def get_compiled_class_by_class_hash(self, class_hash: Hash) -> CasmClass:
        """
        Fetches CasmClass of a contract with given class hash.

        :param class_hash: Class hash of the contract.
        :return: CasmClass of the contract.
        """
        res = await self._feeder_gateway_client.call(
            params={"classHash": hash_to_felt(class_hash)},
            method_name="get_compiled_class_by_class_hash",
        )
        return cast(CasmClass, CasmClassSchema().load(res))

    async def _add_transaction(
        self,
        tx: AccountTransaction,
        token: Optional[str] = None,
    ) -> dict:
        res = await self._gateway_client.post(
            method_name="add_transaction",
            payload=_get_payload(tx),
            params={"token": token} if token is not None else {},
        )
        return res

    async def get_transaction_status(
        self,
        tx_hash: Hash,
    ) -> GatewayTransactionStatusResponse:
        """
        Fetches the transaction's status and block number

        :param tx_hash: Transaction's hash representation
        :return: An object containing transaction's status and optional block hash, if transaction was accepted
        """
        res = await self._feeder_gateway_client.call(
            params={"transactionHash": hash_to_felt(tx_hash)},
            method_name="get_transaction_status",
        )
        if res["tx_status"] in ("UNKNOWN", "NOT_RECEIVED"):
            raise TransactionNotReceivedError()

        return TransactionStatusSchema().load(res)  # pyright: ignore

    async def get_contract_addresses(self) -> dict:
        """
        Fetches the addresses of the Starknet system contracts

        :return: A dictionary indexed with contract name and a value of contract's address
        """
        return await self._feeder_gateway_client.call(
            method_name="get_contract_addresses",
        )

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
            **{"contractAddress": hash_to_felt(contract_address)},
            **block_identifier,
        }

        res = await self._feeder_gateway_client.call(
            method_name="get_code", params=params
        )

        if len(res["bytecode"]) == 0:
            raise ContractNotFoundError(
                address=contract_address,
                block_hash=block_hash,
                block_number=block_number,
            )

        return ContractCodeSchema().load(res, unknown=EXCLUDE)  # pyright: ignore

    async def get_contract_nonce(
        self,
        contract_address: Hash,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        params = {
            **{"contractAddress": hash_to_felt(contract_address)},
            **block_identifier,
        }

        nonce = await self._feeder_gateway_client.call(
            method_name="get_nonce", params=params
        )
        nonce = cast(str, nonce)
        return int(nonce, 16)

    async def get_full_contract(
        self,
        contract_address: Hash,
    ) -> Union[ContractClass, SierraContractClass]:
        res = await self._feeder_gateway_client.call(
            method_name="get_full_contract",
            params={
                "contractAddress": hash_to_felt(contract_address),
            },
        )
        return TypesOfContractClassSchema().load(
            res, unknown=EXCLUDE
        )  # pyright: ignore

    async def get_signature(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> SignatureOnStateDiff:
        """
        Information on what is this signature and how it is calulated here:
        https://community.starknet.io/t/introducing-p2p-authentication-and-mismatch-resolution-in-v0-12-2/97993#signature-on-state-diff-commitment-and-block-hash-3

        :param block_hash: Block's hash or literals `"pending"` or `"latest"`.
        :param block_number: Block's number or literals `"pending"` or `"latest"`.

        :return: Signature on state diff.
        """
        block_identifier = get_block_identifier(
            block_hash=block_hash, block_number=block_number
        )
        res = await self._feeder_gateway_client.call(
            method_name="get_signature",
            params={**block_identifier},
        )
        return SignatureOnStateDiffSchema().load(
            res, unknown=EXCLUDE
        )  # pyright: ignore

    async def get_public_key(self) -> str:
        """
        Method returning current public key.

        :return: Public key.
        """
        public_key = await self._feeder_gateway_client.call(
            method_name="get_public_key"
        )
        return cast(str, public_key)


def get_block_identifier(
    block_hash: Optional[Union[Hash, Tag]] = None,
    block_number: Optional[Union[int, Tag]] = None,
) -> dict:
    if block_hash is not None and block_number is not None:
        raise ValueError(
            "Arguments block_hash and block_number are mutually exclusive."
        )

    if block_hash is not None:
        if is_block_identifier(block_hash):
            return {"blockNumber": block_hash}
        return {"blockHash": hash_to_felt(block_hash)}

    if block_number is not None:
        return {"blockNumber": block_number}

    return {"blockNumber": "pending"}


def _get_payload(
    txs: Union[AccountTransaction, List[AccountTransaction]]
) -> Union[List, Dict]:
    if single_transaction := isinstance(txs, AccountTransaction):
        txs = [txs]

    payload_list = []
    for tx in txs:
        payload = _tx_to_schema(tx).dump(obj=tx)
        assert isinstance(payload, dict)
        if isinstance(tx, DeclareV2):
            payload = compress_program(data=payload, program_name="sierra_program")
        payload_list.append(payload)

    return payload_list if not single_transaction else payload_list[0]


def _tx_to_schema(tx: AccountTransaction):
    if isinstance(tx, Declare):
        return DeclareSchema()
    if isinstance(tx, DeclareV2):
        return DeclareV2Schema()
    if isinstance(tx, DeployAccount):
        return DeployAccountSchema()
    if isinstance(tx, Invoke):
        return InvokeSchema()
    raise ValueError("Invalid tx type.")
