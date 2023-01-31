from abc import ABC, abstractmethod
from typing import List, Optional, Union

from starknet_py.net.client import Client
from starknet_py.net.client_models import (
    Calls,
    Declare,
    DeployAccount,
    Invoke,
    SentTransactionResponse,
)
from starknet_py.net.models import AddressRepresentation
from starknet_py.net.models.typed_data import TypedData


class BaseAccount(ABC):
    """
    Base class for all account implementations.

    Signs, prepares and executes transactions.
    """

    @property
    @abstractmethod
    def address(self) -> int:
        """
        Get the address of the account
        """

    @property
    @abstractmethod
    def client(self) -> Client:
        """
        Get the Client used by the Account.
        """

    @property
    @abstractmethod
    def supported_transaction_version(self) -> int:
        """
        Get transaction version supported by the account.
        """

    @abstractmethod
    async def get_nonce(self) -> int:
        """
        Get the current nonce of the account.

        :return: nonce of the account.
        """

    @abstractmethod
    async def get_balance(
        self, token_address: Optional[AddressRepresentation] = None
    ) -> int:
        """
        Checks account's balance of specified token.

        :param token_address: Address of the ERC20 contract.
            If not specified it will be payment token address.
        :return: Token balance.
        """

    @abstractmethod
    async def sign_for_fee_estimate(
        self, transaction: Union[Invoke, Declare, DeployAccount]
    ) -> Union[Invoke, Declare, DeployAccount]:
        """
        Sign a transaction for a purpose of only fee estimation.
        Should use a transaction version that is not executable on StarkNet,
        calculated like ``transaction.version + 2 ** 128``.

        :param transaction: Transaction to be signed.
        :return: A signed Transaction that can only be used for fee estimation and cannot be executed.
        """

    @abstractmethod
    async def sign_invoke_transaction(
        self,
        calls: Calls,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> Invoke:
        """
        Takes calls and creates signed InvokeFunction.

        :param calls: Single call or list of calls.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: InvokeFunction created from the calls.
        """

    @abstractmethod
    async def sign_declare_transaction(
        self,
        compiled_contract: str,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> Declare:
        """
        Create and sign declare transaction.

        :param compiled_contract: string containing compiled contract bytecode.
            Useful for reading compiled contract from a file.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: Signed Declare transaction.
        """

    @abstractmethod
    async def sign_deploy_account_transaction(
        self,
        class_hash: int,
        contract_address_salt: int,
        constructor_calldata: Optional[List[int]] = None,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeployAccount:
        """
        Create and sign deploy account transaction.

        :param class_hash: Class hash of the contract class to be deployed.
        :param contract_address_salt: A salt used to calculate deployed contract address.
        :param constructor_calldata: Calldata to be ed to contract constructor
            and used to calculate deployed contract address.
        :param max_fee: Max fee to be paid for deploying account transaction. Enough tokens must be prefunded before
            sending the transaction for it to succeed.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: Signed DeployAccount transaction.
        """

    @abstractmethod
    async def execute(
        self,
        calls: Calls,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> SentTransactionResponse:
        """
        Takes calls and executes transaction.

        :param calls: Single call or list of calls.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: SentTransactionResponse.
        """

    @abstractmethod
    def sign_message(self, typed_data: TypedData) -> List[int]:
        """
        Sign an TypedData TypedDict for off-chain usage with the starknet private key and return the signature.
        This adds a message prefix, so it can't be interchanged with transactions.

        :param typed_data: TypedData TypedDict to be signed.
        :return: The signature of the TypedData TypedDict.
        """

    @abstractmethod
    async def verify_message(self, typed_data: TypedData, signature: List[int]) -> bool:
        """
        Verify a signature of a TypedData dict on StarkNet.

        :param typed_data: TypedData TypedDict to be verified.
        :param signature: signature of the TypedData TypedDict.
        :return: true if the signature is valid, false otherwise.
        """
