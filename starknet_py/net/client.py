import asyncio
import typing
from typing import Optional, List, Dict, Union, Any

# noinspection PyPackageRequirements
from services.external_api.client import RetryConfig, BadRequest as BadRequestError
from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    FeederGatewayClient,
    CastableToHash,
    JsonObject,
    TransactionInfo,
)
from starkware.starknet.services.api.feeder_gateway.response_objects import (
    StarknetBlock,
    TransactionReceipt,
)
from starkware.starknet.services.api.gateway.gateway_client import GatewayClient
from starkware.starknet.services.api.gateway.transaction import DECLARE_SENDER_ADDRESS
from starkware.starkware_utils.error_handling import StarkErrorCode

from starknet_py.common import create_compiled_contract
from starknet_py.compile.compiler import StarknetCompilationSource
from starknet_py.constants import TxStatus, ACCEPTED_STATUSES
from starknet_py.net.models.address import BlockIdentifier
from starknet_py.net.models.transaction import Declare
from starknet_py.utils.sync import add_sync_methods
from starknet_py.net.models import (
    InvokeFunction,
    Transaction,
    Deploy,
    StarknetChainId,
    chain_from_network,
)
from starknet_py.net.networks import Network, net_address_from_net
from starknet_py.transaction_exceptions import (
    TransactionFailedError,
    TransactionRejectedError,
    TransactionNotReceivedError,
)

BadRequest = BadRequestError


@add_sync_methods
class Client:
    def __init__(
        self, net: Network, chain: StarknetChainId = None, n_retries: Optional[int] = 1
    ):
        """

        :param net: Target network for the client. Can be a string with URL or one of ``"mainnet"``, ``"testnet"``
        :param chain: Chain used by the network. Required if you use a custom URL for ``net`` param.
        :param n_retries: Number of retries client will attempt before failing a request
        """
        host = net_address_from_net(net)
        retry_config = RetryConfig(n_retries)
        feeder_gateway_url = f"{host}/feeder_gateway"
        self.net = net
        self.chain = chain_from_network(net, chain)
        self._feeder_gateway = FeederGatewayClient(
            url=feeder_gateway_url, retry_config=retry_config
        )

        gateway_url = f"{host}/gateway"
        self._gateway = GatewayClient(url=gateway_url, retry_config=retry_config)

    # View methods
    async def get_contract_addresses(self) -> Dict[str, str]:
        """
        :return: Dictionary containing all of the contract's addresses
        """
        return await self._feeder_gateway.get_contract_addresses()

    async def call_contract(
        self,
        invoke_tx: InvokeFunction,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[BlockIdentifier] = "pending",
    ) -> List[int]:
        """
        Calls the contract with given instance of InvokeTransaction

        :param invoke_tx: The invoke transaction
        :param block_hash: Block hash to execute the contract at specific point of time
        :param block_number: Block number (or "pending" for pending block) to execute the contract at
        :return: List of integers representing contract's function output (structured like calldata)
        """
        response = await self._feeder_gateway.call_contract(
            invoke_tx,
            block_hash,
            block_number,
        )
        return [int(v, 16) for v in response["result"]]

    async def get_block(
        self,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[BlockIdentifier] = "pending",
    ) -> StarknetBlock:
        """
        Retrieve the block's data by its number or hash

        :param block_hash: Block's hash
        :param block_number: Block's number or "pending" for pending block
        :return: Dictionary with block's transactions
        """
        return await self._feeder_gateway.get_block(block_hash, block_number)

    async def get_code(
        self,
        contract_address: int,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[BlockIdentifier] = "pending",
    ) -> dict:
        """
        Retrieve contract's bytecode and abi.

        :raises BadRequest: when contract is not found
        :param contract_address: Address of the contract on Starknet
        :param block_hash: Get code at specific block hash
        :param block_number: Get code at given block number (or "pending" for pending block)
        :return: JSON representation of compiled: {"bytecode": list, "abi": dict}
        """
        code = await self._feeder_gateway.get_code(
            contract_address,
            block_hash,
            block_number,
        )
        code = typing.cast(dict, code)
        if len(code["bytecode"]) == 0:
            raise BadRequest(
                200, f"Contract with address {contract_address} was not found."
            )

        return code

    async def get_storage_at(
        self,
        contract_address: int,
        key: int,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[BlockIdentifier] = "pending",
    ) -> str:
        """
        :param contract_address: Contract's address on Starknet
        :param key: An address of the storage variable inside of the contract.
                    Can be retrieved using ``starkware.starknet.public.abi.get_storage_var_address(<name>)``
        :param block_hash: Fetches the value of the variable at given block hash
        :param block_number: See above, uses block number (or "pending" block) instead of hash
        :return: Storage value of given contract
        """
        return await self._feeder_gateway.get_storage_at(
            contract_address,
            key,
            block_hash,
            block_number,
        )

    async def get_transaction_status(self, tx_hash: CastableToHash) -> JsonObject:
        """
        :param tx_hash: Transaction's hash
        :return: Dictionary containing tx's status
        """
        return await self._feeder_gateway.get_transaction_status(tx_hash)

    async def get_transaction(self, tx_hash: CastableToHash) -> TransactionInfo:
        """
        :param tx_hash: Transaction's hash
        :return: Dictionary representing JSON of the transaction on Starknet
        """
        return await self._feeder_gateway.get_transaction(tx_hash)

    async def get_transaction_receipt(
        self, tx_hash: CastableToHash
    ) -> TransactionReceipt:
        """
        :param tx_hash: Transaction's hash
        :return: Dictionary representing JSON of the transaction's receipt on Starknet
        """
        return await self._feeder_gateway.get_transaction_receipt(tx_hash)

    async def estimate_fee(
        self,
        tx: InvokeFunction,
        block_hash: Optional[CastableToHash] = None,
        block_number: BlockIdentifier = "pending",
    ) -> int:
        """
        Estimate how much Wei it will cost to run passed in transaction

        :param tx: Transaction to estimate
        :param block_hash: Estimate fee at specific block hash
        :param block_number: Estimate fee at given block number (or "pending" for pending block)
        :return: Estimated amount of Wei executing specified transaction will cost
        """
        res = await self._feeder_gateway.estimate_fee(
            invoke_tx=tx, block_hash=block_hash, block_number=block_number
        )
        return res["amount"]

    async def wait_for_tx(
        self,
        tx_hash: Optional[CastableToHash],
        wait_for_accept: Optional[bool] = False,
        check_interval=5,
    ) -> (int, TxStatus):
        """
        Awaits for transaction to get accepted or at least pending by polling its status

        :param tx_hash: Transaction's hash
        :param wait_for_accept: If true waits for ACCEPTED_ONCHAIN status, otherwise waits for at least PENDING
        :param check_interval: Defines interval between checks
        :return: tuple(block number, ``starknet_py.constants.TxStatus``)
        """
        if check_interval <= 0:
            raise ValueError("check_interval has to bigger than 0.")

        first_run = True
        while True:
            result = await self.get_transaction(tx_hash=tx_hash)
            status = result.status

            if status in ACCEPTED_STATUSES:
                return result.block_number, status
            if status == TxStatus.PENDING:
                if not wait_for_accept and result.block_number is not None:
                    return result.block_number, status
            elif status == TxStatus.REJECTED:
                raise TransactionRejectedError(
                    code=result.transaction_failure_reason.code,
                    message=result.transaction_failure_reason.error_message,
                )
            elif status == TxStatus.NOT_RECEIVED:
                if not first_run:
                    raise TransactionNotReceivedError()
            elif status != TxStatus.RECEIVED:
                raise TransactionFailedError()

            first_run = False
            await asyncio.sleep(check_interval)

    # Mutating methods
    async def add_transaction(
        self, tx: Transaction, token: Optional[str] = None
    ) -> Dict[str, str]:
        """
        :param tx: Transaction object (i.e. InvokeFunction, Deploy).
                   A subclass of ``starkware.starknet.services.api.gateway.transaction.Transaction``
        :param token: Optional token for Starknet API access, appended in a query string
        :return: Dictionary with `code`, `transaction_hash`
        """
        return await self._gateway.add_transaction(tx, token)

    async def deploy(
        self,
        compiled_contract: Union[ContractClass, str],
        constructor_calldata: List[int],
        salt: Optional[int] = None,
        version: int = 0,
    ) -> dict:
        if isinstance(compiled_contract, str):
            compiled_contract = ContractClass.loads(compiled_contract)

        res = await self.add_transaction(
            tx=Deploy(
                contract_address_salt=ContractAddressSalt.get_random_value()
                if salt is None
                else salt,
                contract_definition=compiled_contract,
                constructor_calldata=constructor_calldata,
                version=version,
            )
        )

        if res["code"] != StarkErrorCode.TRANSACTION_RECEIVED.name:
            raise TransactionNotReceivedError()
        return res

    async def declare(
        self,
        compilation_source: Optional[StarknetCompilationSource] = None,
        compiled_contract: Optional[str] = None,
        version: int = 0,
        cairo_path: Optional[List[str]] = None,
    ) -> dict:
        """
        Declares contract class.
        Either `compilation_source` or `compiled_contract` is required.

        :param compilation_source: string containing source code or a list of source files paths
        :param compiled_contract: string containing compiled contract. Useful for reading compiled contract from a file
        :param version: PreparedFunctionCall version
        :param cairo_path: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts
        :return: Dictionary with 'transaction_hash' and 'class_hash'
        """
        compiled_contract = create_compiled_contract(
            compilation_source, compiled_contract, cairo_path
        )

        res = await self.add_transaction(
            tx=Declare(
                contract_class=compiled_contract,
                sender_address=DECLARE_SENDER_ADDRESS,
                max_fee=0,
                signature=[],
                nonce=0,
                version=version,
            )
        )

        if res["code"] != StarkErrorCode.TRANSACTION_RECEIVED.name:
            raise TransactionNotReceivedError()

        return res

    async def get_class_hash_at(
        self,
        contract_address: CastableToHash,
        block_hash: Optional[CastableToHash] = None,
        block_number: Optional[BlockIdentifier] = None,
    ) -> str:
        """
        Returns the class hash for a given contract instance address

        :param contract_address: Contract instance address
        :param block_hash: Fetches the value of the variable at given block hash
        :param block_number: See above, uses block number (or "pending" block) instead of hash
        :return: Class hash
        """
        if isinstance(contract_address, str):
            contract_address = int(contract_address, 16)

        return await self._feeder_gateway.get_class_hash_at(
            block_hash=block_hash,
            block_number=block_number,
            contract_address=contract_address,
        )

    async def get_class_by_hash(self, class_hash: CastableToHash) -> Dict[str, Any]:
        """
        Retuns the contract class for given hash

        :param class_hash: Class hash
        :return: Dict with representation of contract class
        """
        if isinstance(class_hash, int):
            class_hash = hex(class_hash)

        return await self._feeder_gateway.get_class_by_hash(class_hash=class_hash)
