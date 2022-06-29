from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Union, Optional, List

from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starknet.services.api.gateway.transaction import DECLARE_SENDER_ADDRESS

from starknet_py.net.client_models import (
    StarknetBlock,
    BlockStateUpdate,
    Transaction,
    TransactionReceipt,
    SentTransaction,
    InvokeFunction,
    StarknetTransaction,
    TransactionStatus,
    Hash,
    Tag,
    DeclaredContract,
    ContractClass,
    Deploy,
    Declare,
)
from starknet_py.net.models import StarknetChainId
from starknet_py.transaction_exceptions import (
    TransactionRejectedError,
    TransactionNotReceivedError,
    TransactionFailedError,
)


class BaseClient(ABC):
    @property
    @abstractmethod
    def chain(self) -> StarknetChainId:
        """
        ChainId of the chain used by the client
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
    async def get_state_update(
        self,
        block_hash: Union[Hash, Tag],
    ) -> BlockStateUpdate:
        """
        Get the information about the result of executing the requested block

        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :return: BlockStateUpdate oject representing changes in the requested block
        """

    @abstractmethod
    async def get_storage_at(
        self,
        contract_address: Hash,
        key: int,
        block_hash: Union[Hash, Tag],
    ) -> int:
        """
        :param contract_address: Contract's address on Starknet
        :param key: An address of the storage variable inside the contract.
        :param block_hash: Fetches the value of the variable at given block hash or at
                           the block indicated by the literals `"pending"` or `"latest"`
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
    async def estimate_fee(
        self,
        tx: InvokeFunction,
        block_hash: Union[Hash, Tag] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
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
        self, invoke_tx: InvokeFunction, block_hash: Union[Hash, Tag] = None
    ) -> List[int]:
        """
        Call the contract with given instance of InvokeTransaction

        :param invoke_tx: Invoke transaction
        :param block_hash: Block hash to execute the contract at specific point of time
                           or at the block indicated by the literals `"pending"` or `"latest"`
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
        :return: SentTransaction object
        """

    async def deploy(
        self,
        contract: Union[ContractClass, str],
        constructor_calldata: List[int],
        salt: Optional[int] = None,
    ) -> SentTransaction:
        """
        Deploy a contract to the network

        :param contract: Contract object or string with compiled contract
        :param constructor_calldata: Data to call the contract constructor with
        :param salt: Salt to be used when signing a transaction
        :return: SentTransaction object
        """
        if isinstance(contract, str):
            contract = ContractClass.loads(contract)

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

        receipt = await self.get_transaction_receipt(tx_hash=res.hash)
        if receipt.status == TransactionStatus.UNKNOWN:
            raise TransactionNotReceivedError()

        return res

    async def declare(self, contract_class: ContractClass) -> SentTransaction:
        """
        Declare a contract

        :param contract_class: Contract class to be declared
        """
        res = await self.add_transaction(
            tx=Declare(
                contract_class=contract_class,
                sender_address=DECLARE_SENDER_ADDRESS,
                max_fee=0,
                signature=[],
                nonce=0,
                version=0,
            )
        )

        receipt = await self.get_transaction_receipt(tx_hash=res.hash)
        if receipt.status == TransactionStatus.UNKNOWN:
            raise TransactionNotReceivedError()

        return res

    @abstractmethod
    async def get_class_hash_at(self, contract_address: Hash) -> int:
        """
        Get the contract class hash for the contract deployed at the given address

        :param contract_address: Address of the contraact whose class hash is to be returned
        :return: Class hash
        """

    @abstractmethod
    async def get_class_by_hash(self, class_hash: Hash) -> DeclaredContract:
        """
        Get the contract class for given class hash

        :param class_hash: Class hash
        :return: ContractClass object
        """
