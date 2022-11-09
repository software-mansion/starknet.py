from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Union, Optional, List, Tuple

from starknet_py.net.client_models import (
    StarknetBlock,
    BlockStateUpdate,
    Transaction,
    TransactionReceipt,
    SentTransactionResponse,
    TransactionStatus,
    Hash,
    Tag,
    DeclaredContract,
    EstimatedFee,
    BlockTransactionTraces,
    DeployTransactionResponse,
    DeclareTransactionResponse,
    Call,
    DeployAccountTransactionResponse,
)
from starknet_py.net.models.transaction import (
    Deploy,
    Declare,
    InvokeFunction,
    DeployAccount,
)
from starknet_py.net.networks import Network
from starknet_py.transaction_exceptions import (
    TransactionRejectedError,
    TransactionNotReceivedError,
    TransactionFailedError,
)
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
class Client(ABC):
    @property
    @abstractmethod
    def net(self) -> Network:
        """
        Network of the client
        """

    @abstractmethod
    async def get_block(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> StarknetBlock:
        """
        Retrieve the block's data by its number or hash

        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: StarknetBlock object representing retrieved block
        """

    @abstractmethod
    async def get_block_traces(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> BlockTransactionTraces:
        """
        Receive the traces of all the transactions within specified block

        :param block_hash: Block's hash
        :param block_number: Block's number or "pending" for pending block
        :return: BlockTransactionTraces object representing received traces
        """

    @abstractmethod
    async def get_state_update(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> BlockStateUpdate:
        """
        Get the information about the result of executing the requested block

        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: BlockStateUpdate oject representing changes in the requested block
        """

    @abstractmethod
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
        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: Storage value of given contract
        """

    @abstractmethod
    async def get_transaction(
        self,
        tx_hash: Hash,
    ) -> Transaction:
        """
        Get the details and status of a submitted transaction

        :param tx_hash: Transaction's hash
        :return: Transaction object
        """

    @abstractmethod
    async def get_transaction_receipt(
        self,
        tx_hash: Hash,
    ) -> TransactionReceipt:
        """
        Get the transaction receipt

        :param tx_hash: Transaction's hash
        :return: Transaction receipt object on Starknet
        """

    async def wait_for_tx(
        self,
        tx_hash: Hash,
        wait_for_accept: Optional[bool] = False,
        check_interval=5,
    ) -> Tuple[int, TransactionStatus]:
        # pylint: disable=too-many-branches
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
        try:
            while True:
                result = await self.get_transaction_receipt(tx_hash=tx_hash)
                status = result.status

                if status in (
                    TransactionStatus.ACCEPTED_ON_L1,
                    TransactionStatus.ACCEPTED_ON_L2,
                ):
                    assert result.block_number is not None
                    return result.block_number, status
                if status == TransactionStatus.PENDING:
                    if not wait_for_accept:
                        if result.block_number is not None:
                            return result.block_number, status
                elif status == TransactionStatus.REJECTED:
                    raise TransactionRejectedError(
                        message=result.rejection_reason,
                    )
                elif status == TransactionStatus.NOT_RECEIVED:
                    if not first_run:
                        raise TransactionNotReceivedError()
                elif status != TransactionStatus.RECEIVED:
                    # This will never get executed with current possible transactions statuses
                    raise TransactionFailedError(
                        message=result.rejection_reason,
                    )

                first_run = False
                await asyncio.sleep(check_interval)
        except asyncio.CancelledError as exc:
            raise TransactionNotReceivedError from exc

    @abstractmethod
    async def estimate_fee(
        self,
        tx: Union[InvokeFunction, Declare, DeployAccount],
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> EstimatedFee:
        """
        Estimate how much Wei it will cost to run provided InvokeFunction

        :param tx: Transaction to estimate
        :param block_hash: Get code at specific block hash or
                           at the block indicated by the literals `"pending"` or `"latest"`
        :param block_number: Get code at given block number or at
                             the block indicated by the literals `"pending"` or `"latest"`
        :return: Estimated amount of Wei executing specified transaction will cost
        """

    @abstractmethod
    async def call_contract(
        self,
        call: Call,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> List[int]:
        """
        Call the contract with given instance of InvokeTransaction

        Warning, InvokeFunction as call_contract parameter has been deprecated in favor of Call.

        :param call: Call
        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: List of integers representing contract's function output (structured like calldata)

        .. versionchanged:: 5.0.0
            Added `Call` as possible invoke_tx type.
            Deprecated InvokeFunction as possible invoke_tx type.
        """

    @abstractmethod
    async def send_transaction(
        self,
        transaction: InvokeFunction,
    ) -> SentTransactionResponse:
        """
        Send a transaction to the network

        :param transaction: Transaction object (i.e. InvokeFunction, Deploy).
        :return: SentTransactionResponse object
        """

    @abstractmethod
    async def deploy(self, transaction: Deploy) -> DeployTransactionResponse:
        """
        Deploy a contract to the network

        :param transaction: Deploy transaction
        :return: SentTransactionResponse object

        .. deprecated:: 0.8.0
            This metod has been deprecated in favor of deploy_prefunded method or deploying through cairo syscall.
        """

    @abstractmethod
    async def deploy_account(
        self, transaction: DeployAccount
    ) -> DeployAccountTransactionResponse:
        """
        Deploy a pre-funded account contract to the network

        :param transaction: DeployAccount transaction
        :return: SentTransactionResponse object
        """

    @abstractmethod
    async def declare(self, transaction: Declare) -> DeclareTransactionResponse:
        """
        Send a declare transaction

        :param transaction: Declare transaction
        :return: SentTransactionResponse object
        """

    @abstractmethod
    async def get_class_hash_at(
        self,
        contract_address: Hash,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        """
        Get the contract class hash for the contract deployed at the given address

        :param contract_address: Address of the contraact whose class hash is to be returned
        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: Class hash
        """

    @abstractmethod
    async def get_class_by_hash(self, class_hash: Hash) -> DeclaredContract:
        """
        Get the contract class for given class hash

        :param class_hash: Class hash
        :return: ContractClass object
        """

    @abstractmethod
    async def get_contract_nonce(
        self,
        contract_address: int,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        """
        Get the latest nonce associated with the given address

        :param contract_address: Get the latest nonce associated with the given address
        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: The last nonce used for the given contract
        """
