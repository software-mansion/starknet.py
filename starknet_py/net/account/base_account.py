from abc import ABC, abstractmethod
from typing import List, Optional, Union

from starknet_py.net.client import Client
from starknet_py.net.client_models import Calls, Hash, SentTransactionResponse, Tag
from starknet_py.net.models import AddressRepresentation, StarknetChainId
from starknet_py.net.models.transaction import (
    Declare,
    DeclareV2,
    DeployAccount,
    Invoke,
    TypeAccountTransaction,
)
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
    async def cairo_version(self) -> int:
        """
        Get Cairo version of the account.
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

            .. deprecated :: 0.15.0
                Property supported_transaction_version is deprecated and will be removed in the future.
        """

    @abstractmethod
    async def get_nonce(
        self,
        *,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        """
        Get the current nonce of the account.

        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: nonce of the account.
        """

    @abstractmethod
    async def get_balance(
        self,
        token_address: Optional[AddressRepresentation] = None,
        chain_id: Optional[StarknetChainId] = None,
        *,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        """
        Checks account's balance of specified token.

        :param token_address: Address of the ERC20 contract.
        :param chain_id: Identifier of the Starknet chain used.
            If token_address is not specified it will be used to determine network's payment token address.
            If token_address is provided, chain_id will be ignored.
        :param block_hash: Block's hash or literals `"pending"` or `"latest"`
        :param block_number: Block's number or literals `"pending"` or `"latest"`
        :return: Token balance.
        """

    @abstractmethod
    async def sign_for_fee_estimate(
        self, transaction: TypeAccountTransaction
    ) -> TypeAccountTransaction:
        """
        Sign a transaction for a purpose of only fee estimation.
        Should use a transaction version that is not executable on Starknet,
        calculated like ``transaction.version + 2 ** 128``.

        :param transaction: Transaction to be signed.
        :return: A signed Transaction that can only be used for fee estimation and cannot be executed.
        """

    @abstractmethod
    async def sign_invoke_transaction(
        self,
        calls: Calls,
        *,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        # TODO (#1184): remove that and docstring
        cairo_version: Optional[int] = None,
    ) -> Invoke:
        """
        Takes calls and creates signed Invoke.

        :param calls: Single call or list of calls.
        :param nonce: Nonce of the transaction.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :param cairo_version:
            Cairo version of the account used.

            .. deprecated:: 0.18.2
                Parameter `cairo_version` has been deprecated - it is calculated automatically based on
                your account's contract class.
        :return: Invoke created from the calls.
        """

    @abstractmethod
    async def sign_declare_transaction(
        self,
        compiled_contract: str,
        *,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> Declare:
        """
        Create and sign declare transaction.

        :param compiled_contract: string containing a compiled Starknet contract. Supports old contracts.
        :param nonce: Nonce of the transaction.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: Signed Declare transaction.
        """

    @abstractmethod
    async def sign_declare_v2_transaction(
        self,
        compiled_contract: str,
        compiled_class_hash: int,
        *,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeclareV2:
        """
        Create and sign declare transaction using sierra contract.

        :param compiled_contract: string containing a compiled Starknet contract.
            Supports new contracts (compiled to sierra).
        :param compiled_class_hash: a class hash of the sierra compiled contract used in the declare transaction.
            Computed from casm compiled contract.
        :param nonce: Nonce of the transaction.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: Signed DeclareV2 transaction.
        """

    @abstractmethod
    async def sign_deploy_account_transaction(
        self,
        class_hash: int,
        contract_address_salt: int,
        constructor_calldata: Optional[List[int]] = None,
        *,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeployAccount:
        """
        Create and sign deploy account transaction.

        :param class_hash: Class hash of the contract class to be deployed.
        :param contract_address_salt: A salt used to calculate deployed contract address.
        :param constructor_calldata: Calldata to be ed to contract constructor
            and used to calculate deployed contract address.
        :param nonce: Nonce of the transaction.
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
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        # TODO (#1184): remove that and docstring
        cairo_version: Optional[int] = None,
    ) -> SentTransactionResponse:
        """
        Takes calls and executes transaction.

        :param calls: Single call or list of calls.
        :param nonce: Nonce of the transaction.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :param cairo_version:
            Cairo version of the account used.

            .. deprecated:: 0.18.2
                Parameter `cairo_version` has been deprecated - it is calculated automatically based on
                your account's contract class.
        :return: SentTransactionResponse.
        """

    @abstractmethod
    def sign_message(self, typed_data: TypedData) -> List[int]:
        """
        Sign an TypedData TypedDict for off-chain usage with the Starknet private key and return the signature.
        This adds a message prefix, so it can't be interchanged with transactions.

        :param typed_data: TypedData TypedDict to be signed.
        :return: The signature of the TypedData TypedDict.
        """

    @abstractmethod
    def verify_message(self, typed_data: TypedData, signature: List[int]) -> bool:
        """
        Verify a signature of a TypedData dict on Starknet.

        :param typed_data: TypedData TypedDict to be verified.
        :param signature: signature of the TypedData TypedDict.
        :return: true if the signature is valid, false otherwise.
        """
