from __future__ import annotations

import asyncio
import warnings
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    BlockStateUpdate,
    BlockTransactionTraces,
    Call,
    ContractClass,
    DeclareTransactionResponse,
    DeployAccountTransactionResponse,
    EstimatedFee,
    Hash,
    SentTransactionResponse,
    SierraContractClass,
    StarknetBlock,
    Tag,
    Transaction,
    TransactionExecutionStatus,
    TransactionFinalityStatus,
    TransactionReceipt,
    TransactionStatus,
)
from starknet_py.net.models.transaction import (
    AccountTransaction,
    Declare,
    DeclareV2,
    DeployAccount,
    Invoke,
)
from starknet_py.net.networks import Network
from starknet_py.transaction_errors import (
    TransactionNotReceivedError,
    TransactionRejectedError,
    TransactionRevertedError,
)
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
class Client(ABC):
    @property
    @abstractmethod
    def net(self) -> Network:
        """
        Network of the client.

         .. deprecated:: 0.15.0
            Property net of the Client interface is deprecated.
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
        :return: BlockStateUpdate object representing changes in the requested block
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

    # https://community.starknet.io/t/efficient-utilization-of-sequencer-capacity-in-starknet-v0-12-1/95607
    async def wait_for_tx(
        self,
        tx_hash: Hash,
        wait_for_accept: Optional[bool] = None,  # pylint: disable=unused-argument
        check_interval: float = 2,
        retries: int = 500,
    ) -> TransactionReceipt:
        # pylint: disable=too-many-branches
        """
        Awaits for transaction to get accepted or at least pending by polling its status.

        :param tx_hash: Transaction's hash.
        :param wait_for_accept:
            .. deprecated:: 0.17.0
                Parameter `wait_for_accept` has been deprecated - since Starknet 0.12.0, transactions in a PENDING
                block have status ACCEPTED_ON_L2.
        :param check_interval: Defines interval between checks.
        :param retries: Defines how many times the transaction is checked until an error is thrown.
        :return: Transaction receipt.
        """
        if check_interval <= 0:
            raise ValueError("Argument check_interval has to be greater than 0.")
        if retries <= 0:
            raise ValueError("Argument retries has to be greater than 0.")
        if wait_for_accept is not None:
            warnings.warn(
                "Parameter `wait_for_accept` has been deprecated - since Starknet 0.12.0, transactions in a PENDING"
                " block have status ACCEPTED_ON_L2."
            )

        while True:
            try:
                tx_receipt = await self.get_transaction_receipt(tx_hash=tx_hash)

                deprecated_status = _status_to_finality_execution(tx_receipt.status)
                finality_status = tx_receipt.finality_status or deprecated_status[0]
                execution_status = tx_receipt.execution_status or deprecated_status[1]

                if execution_status == TransactionExecutionStatus.REJECTED:
                    raise TransactionRejectedError(message=tx_receipt.rejection_reason)

                if execution_status == TransactionExecutionStatus.REVERTED:
                    raise TransactionRevertedError(message=tx_receipt.revert_error)

                if execution_status == TransactionExecutionStatus.SUCCEEDED:
                    return tx_receipt

                if finality_status in (
                    TransactionFinalityStatus.ACCEPTED_ON_L2,
                    TransactionFinalityStatus.ACCEPTED_ON_L1,
                ):
                    return tx_receipt

                retries -= 1
                if retries == 0:
                    raise TransactionNotReceivedError()

                await asyncio.sleep(check_interval)

            except asyncio.CancelledError as exc:
                raise TransactionNotReceivedError from exc
            except ClientError as exc:
                if "Transaction hash not found" not in exc.message:
                    raise exc
                retries -= 1
                if retries == 0:
                    raise TransactionNotReceivedError from exc

                await asyncio.sleep(check_interval)

    @abstractmethod
    async def estimate_fee(
        self,
        tx: Union[AccountTransaction, List[AccountTransaction]],
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> Union[EstimatedFee, List[EstimatedFee]]:
        """
        Estimate how much Wei it will cost to run provided transaction.

        :param tx: Transaction to estimate
        :param block_hash: Block's hash or literals `"pending"` or `"latest"`.
        :param block_number: Block's number or literals `"pending"` or `"latest"`.
        :return: Estimated amount of Wei executing specified transaction will cost.
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

        :param call: Call
        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: List of integers representing contract's function output (structured like calldata)
        """

    @abstractmethod
    async def send_transaction(
        self,
        transaction: Invoke,
    ) -> SentTransactionResponse:
        """
        Send a transaction to the network

        :param transaction: Transaction object (i.e. Invoke).
        :return: SentTransactionResponse object
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
    async def declare(
        self, transaction: Union[Declare, DeclareV2]
    ) -> DeclareTransactionResponse:
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

        :param contract_address: Address of the contract whose class hash is to be returned
        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: Class hash
        """

    @abstractmethod
    async def get_class_by_hash(
        self, class_hash: Hash
    ) -> Union[ContractClass, SierraContractClass]:
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


def _status_to_finality_execution(
    status: Optional[TransactionStatus],
) -> Tuple[Optional[TransactionFinalityStatus], Optional[TransactionExecutionStatus]]:
    if status is None:
        return None, None
    finality_statuses = [finality.value for finality in TransactionFinalityStatus]
    if status.value in finality_statuses:
        return TransactionFinalityStatus(status.value), None
    return None, TransactionExecutionStatus(status.value)
