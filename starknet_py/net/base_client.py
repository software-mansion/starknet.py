import asyncio
from abc import ABC, abstractmethod
from typing import Union, Optional, List

# TODO add import based on python version
from typing_extensions import TypedDict

from starknet_py.net.client_models import (
    StarknetBlock,
    BlockState,
    Transaction,
    TransactionReceipt,
    ContractCode,
    SentTransaction,
    InvokeFunction,
    StarknetTransaction,
    ContractDefinition,
    TransactionStatus,
    Hash,
)
from starknet_py.transaction_exceptions import (
    TransactionRejectedError,
    TransactionNotReceivedError,
    TransactionFailedError,
)


class BlockHashIdentifier(TypedDict):
    block_hash: int
    index: int


class BlockNumberIdentifier(TypedDict):
    block_number: int
    index: int


class BaseClient(ABC):
    @abstractmethod
    async def get_block(
        self,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> StarknetBlock:
        """
        Retrieve the block's data by its number or hash

        :param block_hash: Block's hash
        :param block_number: Block's number
        :return: StarknetBlock object representing retrieved block
        """

    @abstractmethod
    async def get_state_update(
        self,
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
    ) -> BlockState:
        """
        # TODO expand specs of this class, create proper dataclass
        Get the information about the result of executing the requested block

        :param block_hash: Block's hash
        :param block_number: Block's number
        :return: JsonObject object representing retrieved block
        """

    @abstractmethod
    async def get_storage_at(
        self,
        contract_address: Hash,
        key: int,
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
    ) -> int:
        """
        :param contract_address: Contract's address on Starknet
        :param key: An address of the storage variable inside the contract.
        :param block_hash: Fetches the value of the variable at given block hash
        :param block_number: See above, uses block number instead of hash
        :return: Storage value of given contract
        """

    @abstractmethod
    async def get_transaction(
        self,
        tx_identifier: Union[Hash, BlockHashIdentifier, BlockNumberIdentifier],
    ) -> Transaction:
        """
        Get the details and status of a submitted transaction

        :param tx_identifier: Transaction's identifier
        :return: Dictionary representing JSON of the transaction on Starknet
        """

    @abstractmethod
    async def get_transaction_receipt(
        self,
        tx_hash: Hash,
    ) -> TransactionReceipt:
        """
        Get the transaction receipt

        :param tx_hash: Transaction's hash
        :return: Dictionary representing JSON of the transaction's receipt on Starknet
        """

    @abstractmethod
    async def get_code(
        self,
        contract_address: Hash,
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
    ) -> ContractCode:
        """
        Get deployed contract's bytecode and abi.

        :raises BadRequest: when contract is not found
        :param contract_address: Address of the contract on Starknet
        :param block_hash: Get code at specific block hash
        :param block_number: Get code at given block number (or "pending" for pending block)
        :return: JSON representation of compiled: {"bytecode": list, "abi": dict}
        """

    async def wait_for_tx(
        self,
        tx_hash: Hash,
        wait_for_accept: Optional[bool] = False,
        check_interval=5,
    ) -> (int, TransactionStatus):
        """
        Awaits for transaction to get accepted or at least pending by polling its status

        :param tx_hash: Transaction's hash
        :param wait_for_accept: If true waits for at least ACCEPTED_ON_L2 status, otherwise waits for at least PENDING
        :param check_interval: Defines interval between checks
        :return: Tuple containing block number and transaction status
        """
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

    @abstractmethod
    async def estimate_fee(self, tx: InvokeFunction) -> int:
        """
        Estimate how much Wei it will cost to run provided InvokeFunction

        :param tx: Transaction to estimate
        :return: Estimated amount of Wei executing specified transaction will cost
        """

    @abstractmethod
    async def call_contract(
        self,
        invoke_tx: InvokeFunction,
        block_hash: Optional[Hash] = None,
        block_number: Optional[int] = None,
    ) -> List[int]:
        """
        Call the contract with given instance of InvokeTransaction

        :param invoke_tx: Invoke transaction
        :param block_hash: Block hash to execute the contract at specific point of time
        :param block_number: Block number (or "pending" for pending block) to execute the contract at
        :return: List of integers representing contract's function output (structured like calldata)
        """

    @abstractmethod
    async def add_transaction(
        self,
        tx: StarknetTransaction,
    ) -> SentTransaction:
        """
        Send a transaction to the network

        :param tx: Transaction object (i.e. InvokeFunction, Deploy).
        :return: Dictionary with `code`, `transaction_hash`
        """

    @abstractmethod
    async def deploy(
        self,
        contract: Union[ContractDefinition, str],
        constructor_calldata: List[int],
        salt: Optional[int] = None,
    ) -> SentTransaction:
        """
        Deploy a contract to the network

        :param contract: Contract object or string with compiled contract
        :param constructor_calldata: Data to call the contract constructor with
        :param salt: Salt to be used when signing a transaction
        return: Dict with result of the transaction deployment
        """
