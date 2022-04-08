from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union, Optional, List

from starknet_py.net.client_models import (
    StarknetBlock,
    BlockState,
    Transaction,
    TransactionReceipt,
    ContractCode,
    FunctionCall,
    SentTransaction,
)
from starknet_py.contract import Contract


@dataclass
class BlockHashIdentifier:
    block_hash: int
    index: int


@dataclass
class BlockNumberIdentifier:
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
        block_hash: Optional[Union[int, str]] = None,
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
        contract_address: int,
        key: int,
        block_hash: Optional[Union[int, str]] = None,
        block_number: Optional[int] = None,
    ) -> str:
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
        tx_identifier: Union[
            Union[int, str], BlockHashIdentifier, BlockNumberIdentifier
        ],
    ) -> Transaction:
        """
        Get the details and status of a submitted transaction

        :param tx_identifier: Transaction's identifier
        :return: Dictionary representing JSON of the transaction on Starknet
        """

    @abstractmethod
    async def get_transaction_receipt(
        self,
        tx_hash: Union[int, str],
    ) -> TransactionReceipt:
        """
        Get the transaction receipt

        :param tx_hash: Transaction's hash
        :return: Dictionary representing JSON of the transaction's receipt on Starknet
        """

    @abstractmethod
    async def get_code(
        self,
        contract_address: Union[int, str],
        block_hash: Optional[Union[int, str]] = None,
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

    @abstractmethod
    async def call_contract(
        self,
        invoke_tx: FunctionCall,
        block_hash: Optional[Union[int, str]] = None,
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
        tx: Transaction,
    ) -> SentTransaction:
        """
        Send a transaction to the network

        :param tx: Transaction object (i.e. InvokeFunction, Deploy).
        :return: Dictionary with `code`, `transaction_hash`
        """

    @abstractmethod
    async def deploy(
        self,
        contract: Contract,
        constructor_calldata: List[int],
        salt: Optional[int] = None,
    ) -> SentTransaction:
        """
        Deploy a contract to the network

        :param contract: Contract object
        :param constructor_calldata: Data to call the contract constructor with
        :param salt: Salt to be used when signing a transaction
        return: Dict with result of the transaction deployment
        """
