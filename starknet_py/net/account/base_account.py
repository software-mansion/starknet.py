from abc import ABC, abstractmethod
from typing import List, Optional, Union

from starknet_py.constants import ANY_CALLER, OutsideExecutionInterfaceID
from starknet_py.net.client import Client
from starknet_py.net.client_models import (
    Call,
    Calls,
    EstimatedFee,
    Hash,
    OutsideExecutionTimeBounds,
    ResourceBounds,
    SentTransactionResponse,
    Tag,
)
from starknet_py.net.models import AddressRepresentation
from starknet_py.net.models.transaction import (
    AccountTransaction,
    DeclareV1,
    DeclareV2,
    DeclareV3,
    DeployAccountV1,
    DeployAccountV3,
    InvokeV1,
    InvokeV3,
    TypeAccountTransaction,
)
from starknet_py.net.models.typed_data import TypedDataDict


class OutsideExecutionSupportBaseMixin(ABC):

    @abstractmethod
    async def get_outside_execution_nonce(self) -> int:
        """
        Generate special valid nonce for outside execution calls.
        """

    @abstractmethod
    async def supports_interface(
        self, interface_id: OutsideExecutionInterfaceID
    ) -> bool:
        """
        Check if the account supports the given outside execution interface. Part of ISRC5 standard.
        """

    @abstractmethod
    async def sign_outside_execution_call(
        self,
        calls: Calls,
        execution_time_bounds: OutsideExecutionTimeBounds,
        *,
        caller: AddressRepresentation = ANY_CALLER,
        nonce: Optional[int] = None,
        interface_version: Optional[OutsideExecutionInterfaceID] = None,
    ) -> Call:
        """
        Creates a call for an outcide execution (SNIP-9 specification).

        :param calls: Single call or list of calls to be executed by outside caller.
        :param execution_time_bounds: Execution time bounds for the call.
        :param caller: Address of the caller. IMPORTANT! By default it is ANY_CALLER.
        :param nonce: Nonce for the transaction. Is populated automatically if not provided.
        :param interface_version: Outside execution interface version. Method will check which version account
            supports and use the highest one and populate the value.
        """


class BaseAccount(OutsideExecutionSupportBaseMixin, ABC):
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

    @abstractmethod
    async def estimate_fee(
        self,
        tx: Union[AccountTransaction, List[AccountTransaction]],
        skip_validate: bool = False,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> Union[EstimatedFee, List[EstimatedFee]]:
        """
        Estimates the resources required by a given sequence of transactions when applied on a given state.
        If one of the transactions reverts or fails due to any reason (e.g. validation failure or an internal error),
        a TRANSACTION_EXECUTION_ERROR is returned.
        For v0-2 transactions the estimate is given in Wei, and for v3 transactions it is given in Fri.

        :param tx: Transaction or list of transactions to estimate
        :param skip_validate: Flag checking whether the validation part of the transaction should be executed
        :param block_hash: Block hash or literals `"pending"` or `"latest"`
        :param block_number: Block number or literals `"pending"` or `"latest"`
        :return: Estimated fee or list of estimated fees for each transaction
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
        *,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> int:
        """
        Checks account's balance of the specified token.
        By default, it uses the L2 ETH address for mainnet and sepolia networks.

        :param token_address: Address of the ERC20 contract.
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
    async def sign_invoke_v1(
        self,
        calls: Calls,
        *,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> InvokeV1:
        """
        Takes calls and creates signed Invoke.

        .. deprecated:: 0.25.0
           This method is deprecated and will be removed in future versions.
           Use :py:meth:`stanet_py.net.account.BaseAccount.sign_invoke_v3` instead.

        :param calls: Single call or list of calls.
        :param nonce: Nonce of the transaction.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: Invoke created from the calls.
        """

    @abstractmethod
    async def sign_invoke_v3(
        self,
        calls: Calls,
        *,
        nonce: Optional[int] = None,
        l1_resource_bounds: Optional[ResourceBounds] = None,
        auto_estimate: bool = False,
    ) -> InvokeV3:
        """
        Takes calls and creates signed Invoke.

        :param calls: Single call or list of calls.
        :param nonce: Nonce of the transaction.
        :param l1_resource_bounds: Max amount and max price per unit of L1 gas used in this transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: Invoke created from the calls.
        """

    # pylint: disable=line-too-long
    @abstractmethod
    async def sign_declare_v1(
        self,
        compiled_contract: str,
        *,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeclareV1:
        """
        .. deprecated:: 0.25.0
           This method is deprecated and will be removed in future versions.
           Use :py:meth:`stanet_py.net.account.BaseAccount.sign_declare_v3` instead.

        Based on https://docs.starknet.io/architecture-and-concepts/network-architecture/transactions/#transaction_versioning

        :param compiled_contract: string containing a compiled Starknet contract. Supports old contracts.
        :param nonce: Nonce of the transaction.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: Signed Declare transaction.
        """

    # pylint: enable=line-too-long

    @abstractmethod
    async def sign_declare_v2(
        self,
        compiled_contract: str,
        compiled_class_hash: int,
        *,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeclareV2:
        """
        Create and sign declare transaction version 2 using sierra contract.

        .. deprecated:: 0.25.0
           This method is deprecated and will be removed in future versions.
           Use :py:meth:`stanet_py.net.account.BaseAccount.sign_declare_v3` instead.

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
    async def sign_declare_v3(
        self,
        compiled_contract: str,
        compiled_class_hash: int,
        *,
        nonce: Optional[int] = None,
        l1_resource_bounds: Optional[ResourceBounds] = None,
        auto_estimate: bool = False,
    ) -> DeclareV3:
        """
        Create and sign declare transaction version 3 using sierra contract.

        :param compiled_contract: string containing a compiled Starknet contract.
            Supports new contracts (compiled to sierra).
        :param compiled_class_hash: a class hash of the sierra compiled contract used in the declare transaction.
            Computed from casm compiled contract.
        :param nonce: Nonce of the transaction.
        :param l1_resource_bounds: Max amount and max price per unit of L1 gas used in this transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: Signed DeclareV3 transaction.
        """

    @abstractmethod
    async def sign_deploy_account_v1(
        self,
        class_hash: int,
        contract_address_salt: int,
        constructor_calldata: Optional[List[int]] = None,
        *,
        nonce: int = 0,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeployAccountV1:
        # pylint: disable=too-many-arguments
        """
        Create and sign deploy account transaction version 1.

        .. deprecated:: 0.25.0
           This method is deprecated and will be removed in future versions.
           Use :py:meth:`stanet_py.net.account.BaseAccount.sign_deploy_account_v3` instead.

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
    async def sign_deploy_account_v3(
        self,
        class_hash: int,
        contract_address_salt: int,
        *,
        constructor_calldata: Optional[List[int]] = None,
        nonce: int = 0,
        l1_resource_bounds: Optional[ResourceBounds] = None,
        auto_estimate: bool = False,
    ) -> DeployAccountV3:
        # pylint: disable=too-many-arguments
        """
        Create and sign deploy account transaction version 3.

        :param class_hash: Class hash of the contract class to be deployed.
        :param contract_address_salt: A salt used to calculate deployed contract address.
        :param constructor_calldata: Calldata to be ed to contract constructor
            and used to calculate deployed contract address.
        :param nonce: Nonce of the transaction.
        :param l1_resource_bounds: Max amount and max price per unit of L1 gas used in this transaction.
            Enough tokens must be prefunded before sending the transaction for it to succeed.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: Signed DeployAccountV3 transaction.
        """

    @abstractmethod
    async def execute_v1(
        self,
        calls: Calls,
        *,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> SentTransactionResponse:
        """
        Takes calls and executes transaction.

        :param calls: Single call or list of calls.
        :param nonce: Nonce of the transaction.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: SentTransactionResponse.
        """

    @abstractmethod
    async def execute_v3(
        self,
        calls: Calls,
        *,
        l1_resource_bounds: Optional[ResourceBounds] = None,
        nonce: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> SentTransactionResponse:
        """
        Takes calls and executes transaction.

        :param calls: Single call or list of calls.
        :param l1_resource_bounds: Max amount and max price per unit of L1 gas used in this transaction.
        :param nonce: Nonce of the transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: SentTransactionResponse.
        """

    @abstractmethod
    def sign_message(self, typed_data: TypedDataDict) -> List[int]:
        """
        Sign an TypedData TypedDict for off-chain usage with the Starknet private key and return the signature.
        This adds a message prefix, so it can't be interchanged with transactions.
        Both v0 and v1 domain revision versions are supported.

        :param typed_data: TypedData TypedDict to be signed.
        :return: The signature of the TypedData TypedDict.
        """

    @abstractmethod
    def verify_message(self, typed_data: TypedDataDict, signature: List[int]) -> bool:
        """
        Verify a signature of a TypedData dict on Starknet.
        Both v0 and v1 domain revision versions are supported.

        :param typed_data: TypedData TypedDict to be verified.
        :param signature: signature of the TypedData TypedDict.
        :return: true if the signature is valid, false otherwise.
        """
