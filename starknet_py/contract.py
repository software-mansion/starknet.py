from __future__ import annotations

import dataclasses
import warnings
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional, Tuple, TypeVar, Union

from starkware.cairo.lang.compiler.identifier_manager import IdentifierManager
from starkware.starknet.core.os.class_hash import compute_class_hash
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.public.abi_structs import identifier_manager_from_abi

from starknet_py.abi.model import Abi
from starknet_py.abi.parser import AbiParser
from starknet_py.common import create_compiled_contract
from starknet_py.compile.compiler import StarknetCompilationSource
from starknet_py.constants import DEFAULT_DEPLOYER_ADDRESS
from starknet_py.net import AccountClient
from starknet_py.net.account._account_proxy import AccountProxy
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client import Client
from starknet_py.net.client_models import Call, Hash, Tag
from starknet_py.net.models import (
    AddressRepresentation,
    Invoke,
    compute_address,
    parse_address,
)
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.proxy.contract_abi_resolver import (
    ContractAbiResolver,
    ProxyConfig,
    prepare_proxy_config,
)
from starknet_py.serialization import TupleDataclass, serializer_for_function
from starknet_py.serialization.function_serialization_adapter import (
    FunctionSerializationAdapter,
)
from starknet_py.utils.contructor_args_translator import translate_constructor_args
from starknet_py.utils.crypto.facade import pedersen_hash
from starknet_py.utils.sync import add_sync_methods

ABI = list
ABIEntry = dict
TSentTransaction = TypeVar("TSentTransaction", bound="SentTransaction")


@dataclass(frozen=True)
class ContractData:
    address: int
    abi: ABI

    @cached_property
    def identifier_manager(self) -> IdentifierManager:
        warnings.warn(
            "Using identifier_manager from ContractData has been deprecated. Consider using parsed_abi instead."
        )
        return identifier_manager_from_abi(self.abi)

    @cached_property
    def parsed_abi(self) -> Abi:
        """
        Abi parsed into proper dataclass.
        :return: Abi
        """
        return AbiParser(self.abi).parse()

    @staticmethod
    def from_abi(address: int, abi: ABI) -> ContractData:
        return ContractData(
            address=address,
            abi=abi,
        )


@add_sync_methods
@dataclass(frozen=True)
class SentTransaction:
    """
    Dataclass exposing the interface of transaction related to a performed action.
    """

    hash: int
    """Hash of the transaction."""

    _client: Client
    status: Optional[str] = None
    """Status of the transaction."""

    block_number: Optional[int] = None
    """Number of the block in which transaction was included."""

    async def wait_for_acceptance(
        self: TSentTransaction,
        wait_for_accept: Optional[bool] = False,
        check_interval=5,
    ) -> TSentTransaction:
        """
        Waits for transaction to be accepted on chain. By default, returns when status is ``PENDING`` -
        use ``wait_for_accept`` to wait till ``ACCEPTED`` status.
        Returns a new SentTransaction instance, **does not mutate original instance**.
        """
        block_number, status = await self._client.wait_for_tx(
            self.hash,
            wait_for_accept=wait_for_accept,
            check_interval=check_interval,
        )
        return dataclasses.replace(
            self,
            status=status,
            block_number=block_number,
        )


@add_sync_methods
@dataclass(frozen=True)
class InvokeResult(SentTransaction):
    """
    Result of the Invoke transaction.
    """

    # We ensure these are not None in __post_init__
    contract: ContractData = None  # pyright: ignore
    """Additional information about the Contract that made the transaction."""

    invoke_transaction: Invoke = None  # pyright: ignore
    """A InvokeTransaction instance used."""

    def __post_init__(self):
        assert self.contract is not None
        assert self.invoke_transaction is not None


InvocationResult = InvokeResult


@add_sync_methods
@dataclass(frozen=True)
class DeclareResult(SentTransaction):
    """
    Result of the Declare transaction.
    """

    _account: BaseAccount = None  # pyright: ignore

    class_hash: int = None  # pyright: ignore
    """Class hash of the declared contract."""

    compiled_contract: str = None  # pyright: ignore
    """Compiled contract that was declared."""

    def __post_init__(self):
        if self._account is None:
            raise ValueError("Argument _account can't be None.")

        if self.class_hash is None:
            raise ValueError("Argument class_hash can't be None.")

        if self.compiled_contract is None:
            raise ValueError("Argument compiled_contract can't be None.")

    async def deploy(
        self,
        *,
        deployer_address: AddressRepresentation = DEFAULT_DEPLOYER_ADDRESS,
        salt: Optional[int] = None,
        unique: bool = True,
        constructor_args: Optional[Union[List, Dict]] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> "DeployResult":
        """
        Deploys a contract.

        :param deployer_address: Address of the UDC. Is set to the address of
            the default UDC (same address on mainnet/testnet/devnet) by default.
            Must be set when using custom network other than ones listed above.
        :param salt: Optional salt. Random value is selected if it is not provided.
        :param unique: Determines if the contract should be salted with the account address.
        :param constructor_args: a ``list`` or ``dict`` of arguments for the constructor.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :return: DeployResult instance.
        """
        # pylint: disable=too-many-arguments
        abi = create_compiled_contract(compiled_contract=self.compiled_contract).abi

        deployer = Deployer(
            deployer_address=deployer_address,
            account_address=self._account.address if unique else None,
        )
        deploy_call, address = deployer.create_deployment_call(
            class_hash=self.class_hash, salt=salt, abi=abi, calldata=constructor_args
        )
        res = await self._account.execute(
            calls=deploy_call, max_fee=max_fee, auto_estimate=auto_estimate
        )

        deployed_contract = Contract(
            provider=self._account,
            address=address,
            abi=abi,
        )

        deploy_result = DeployResult(
            hash=res.transaction_hash,
            _client=self._account.client,
            deployed_contract=deployed_contract,
        )

        return deploy_result


@add_sync_methods
@dataclass(frozen=True)
class DeployResult(SentTransaction):
    """
    Result of the contract deployment.
    """

    # We ensure this is not None in __post_init__
    deployed_contract: Contract = None  # pyright: ignore
    """A Contract instance representing the deployed contract."""

    def __post_init__(self):
        if self.deployed_contract is None:
            raise ValueError("Argument deployed_contract can't be None.")


# pylint: disable=too-many-instance-attributes
@add_sync_methods
class PreparedFunctionCall(Call):
    def __init__(
        self,
        calldata: List[int],
        selector: int,
        client: Client,
        account: Optional[BaseAccount],
        payload_transformer: FunctionSerializationAdapter,
        contract_data: ContractData,
        max_fee: Optional[int],
        version: int,
    ):
        # pylint: disable=too-many-arguments
        super().__init__(
            to_addr=contract_data.address, selector=selector, calldata=calldata
        )
        self._client = client
        self._internal_account = account
        self._payload_transformer = payload_transformer
        self._contract_data = contract_data
        self.max_fee = max_fee
        self.version = version

    @property
    def _account(self) -> BaseAccount:
        if self._internal_account is not None:
            return self._internal_account

        raise ValueError(
            "Contract was created without Account or with Client that is not an account."
        )

    async def call_raw(
        self,
        block_hash: Optional[str] = None,
    ) -> List[int]:
        """
        Calls a method without translating the result into python values.

        :param block_hash: Optional block hash.
        :return: list of ints.
        """
        return await self._client.call_contract(call=self, block_hash=block_hash)

    async def call(
        self,
        block_hash: Optional[str] = None,
    ) -> TupleDataclass:
        """
        Calls a method.

        :param block_hash: Optional block hash.
        :return: CallResult or List[int] if return_raw is used.
        """
        result = await self.call_raw(block_hash=block_hash)
        return self._payload_transformer.deserialize(result)

    async def invoke(
        self,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> InvokeResult:
        """
        Invokes a method.

        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :return: InvokeResult.
        """
        if max_fee is not None:
            self.max_fee = max_fee

        transaction = await self._account.sign_invoke_transaction(
            calls=self,
            max_fee=self.max_fee,
            auto_estimate=auto_estimate,
        )

        response = await self._client.send_transaction(transaction)

        invoke_result = InvokeResult(
            hash=response.transaction_hash,  # noinspection PyTypeChecker
            _client=self._client,
            contract=self._contract_data,
            invoke_transaction=transaction,
        )

        return invoke_result

    async def estimate_fee(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ):
        """
        Estimate fee for prepared function call.

        :param block_hash: Estimate fee at specific block hash.
        :param block_number: Estimate fee at given block number
            (or "latest" / "pending" for the latest / pending block), default is "pending".
        :return: Estimated amount of Wei executing specified transaction will cost.
        """
        tx = await self._account.sign_invoke_transaction(calls=self, max_fee=0)

        return await self._client.estimate_fee(
            tx=tx, block_hash=block_hash, block_number=block_number
        )


@add_sync_methods
class ContractFunction:
    def __init__(
        self,
        name: str,
        abi: ABIEntry,
        contract_data: ContractData,
        client: Client,
        account: Optional[BaseAccount],
    ):
        # pylint: disable=too-many-arguments
        self.name = name
        self.abi = abi
        self.inputs = abi["inputs"]
        self.contract_data = contract_data
        self.client = client
        self.account = account
        self._payload_transformer = serializer_for_function(
            contract_data.parsed_abi.functions[name]
        )

    def prepare(
        self,
        *args,
        max_fee: Optional[int] = None,
        **kwargs,
    ) -> PreparedFunctionCall:
        """
        ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        Creates a ``PreparedFunctionCall`` instance which exposes calldata for every argument
        and adds more arguments when calling methods.

        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :return: PreparedFunctionCall.
        """
        version = (
            self.account.supported_transaction_version
            if self.account is not None
            else 0
        )

        if version == 0:
            warnings.warn(
                "Transaction with version 0 is deprecated and will be removed in the future. "
                "Use AccountClient supporting the transaction version 1",
                category=DeprecationWarning,
            )

        calldata = self._payload_transformer.serialize(*args, **kwargs)
        return PreparedFunctionCall(
            calldata=calldata,
            contract_data=self.contract_data,
            client=self.client,
            account=self.account,
            payload_transformer=self._payload_transformer,
            selector=self.get_selector(self.name),
            max_fee=max_fee,
            version=version,
        )

    async def call(
        self,
        *args,
        block_hash: Optional[str] = None,
        **kwargs,
    ) -> TupleDataclass:
        """
        Call contract's function. ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        The result is translated from Cairo data to python values.
        Equivalent of ``.prepare(*args, **kwargs).call()``.

        :param block_hash: Block hash to perform the call to the contract at specific point of time.
        """
        return await self.prepare(max_fee=0, *args, **kwargs).call(
            block_hash=block_hash
        )

    async def invoke(
        self,
        *args,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        **kwargs,
    ) -> InvokeResult:
        """
        Invoke contract's function. ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        Equivalent of ``.prepare(*args, **kwargs).invoke()``.

        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        """
        prepared_call = self.prepare(*args, **kwargs)
        return await prepared_call.invoke(max_fee=max_fee, auto_estimate=auto_estimate)

    @staticmethod
    def get_selector(function_name: str):
        """
        :param function_name: Contract function's name.
        :return: A StarkNet integer selector for this function inside the contract.
        """
        return get_selector_from_name(function_name)


FunctionsRepository = Dict[str, ContractFunction]


@add_sync_methods
class Contract:
    """
    Cairo contract's model.
    """

    def __init__(
        self,
        address: AddressRepresentation,
        abi: list,
        provider: Union[BaseAccount, Client] = None,  # pyright: ignore
        *,
        client: Optional[Client] = None,
    ):
        """
        Should be used instead of ``from_address`` when ABI is known statically.

        Arguments account and client are mutually exclusive and cannot be provided at the same time.

        :param address: contract's address.
        :param abi: contract's abi.
        :param provider: BaseAccount or Client used to perform transactions.
        :param client: client used to perform transactions.
        """
        client, account = _unpack_provider(provider, client)

        self.account: Optional[BaseAccount] = account
        self.client: Client = client
        self.data = ContractData.from_abi(parse_address(address), abi)
        self._functions = self._make_functions(self.data, self.client, self.account)

    @property
    def functions(self) -> FunctionsRepository:
        """
        :return: All functions exposed from a contract.
        """
        return self._functions

    @property
    def address(self) -> int:
        """Address of the contract."""
        return self.data.address

    @staticmethod
    async def from_address(
        address: AddressRepresentation,
        provider: Union[BaseAccount, Client] = None,  # pyright: ignore
        proxy_config: Union[bool, ProxyConfig] = False,
        *,
        client: Optional[Client] = None,
    ) -> Contract:
        """
        Fetches ABI for given contract and creates a new Contract instance with it. If you know ABI statically you
        should create Contract's instances directly instead of using this function to avoid unnecessary API calls.

        :raises ContractNotFoundError: when contract is not found.
        :raises TypeError: when given client's `get_class_by_hash` method does not return abi.
        :raises ProxyResolutionError: when given ProxyChecks were not sufficient to resolve proxy's implementation.
        :param address: Contract's address.
        :param provider: BaseAccount or Client.
        :param proxy_config: Proxy resolving config
            If set to ``True``, will use default proxy checks
            :class:`starknet_py.proxy.proxy_check.OpenZeppelinProxyCheck`
            and :class:`starknet_py.proxy.proxy_check.ArgentProxyCheck`.

            If set to ``False``, :meth:`Contract.from_address` will not resolve proxies.

            If a valid :class:`starknet_py.contract_abi_resolver.ProxyConfig` is provided, will use its values instead.
        :param client: Client.

        :return: an initialized Contract instance.
        """
        client, account = _unpack_provider(provider, client)

        address = parse_address(address)
        proxy_config = Contract._create_proxy_config(proxy_config)

        abi = await ContractAbiResolver(
            address=address, client=client, proxy_config=proxy_config
        ).resolve()

        return Contract(address=address, abi=abi, provider=account or client)

    @staticmethod
    async def declare(
        account: Union[AccountClient, BaseAccount],
        compiled_contract: str,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeclareResult:
        """
        Declares a contract.

        :param account: An AccountClient used to sign and send declare transaction.
        :param compiled_contract: String containing compiled contract.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :return: DeclareResult instance.
        """
        account = _account_or_proxy(account)

        declare_tx = await account.sign_declare_transaction(
            compiled_contract=compiled_contract,
            max_fee=max_fee,
            auto_estimate=auto_estimate,
        )
        res = await account.client.declare(transaction=declare_tx)

        return DeclareResult(
            hash=res.transaction_hash,
            _client=account.client,
            class_hash=res.class_hash,
            _account=account,
            compiled_contract=compiled_contract,
        )

    @staticmethod
    async def deploy_contract(
        account: Union[AccountClient, BaseAccount],
        class_hash: Hash,
        abi: List,
        constructor_args: Optional[Union[List, Dict]] = None,
        *,
        deployer_address: AddressRepresentation = DEFAULT_DEPLOYER_ADDRESS,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> "DeployResult":
        """
        Deploys a contract through Universal Deployer Contract

        :param account: An AccountClient used to sign and send deploy transaction.
        :param class_hash: The class_hash of the contract to be deployed.
        :param abi: An abi of the contract to be deployed.
        :param constructor_args: a ``list`` or ``dict`` of arguments for the constructor.
        :param deployer_address: Address of the UDC. Is set to the address of
            the default UDC (same address on mainnet/testnet/devnet) by default.
            Must be set when using custom network other than ones listed above.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :return: DeployResult instance.
        """
        # pylint: disable=too-many-arguments
        account = _account_or_proxy(account)

        deployer = Deployer(
            deployer_address=deployer_address, account_address=account.address
        )
        deploy_call, address = deployer.create_deployment_call(
            class_hash=class_hash, abi=abi, calldata=constructor_args
        )
        res = await account.execute(
            calls=deploy_call, max_fee=max_fee, auto_estimate=auto_estimate
        )

        deployed_contract = Contract(
            provider=account,
            address=address,
            abi=abi,
        )
        deploy_result = DeployResult(
            hash=res.transaction_hash,
            _client=account.client,
            deployed_contract=deployed_contract,
        )

        return deploy_result

    @staticmethod
    def compute_address(
        salt: int,
        compilation_source: Optional[StarknetCompilationSource] = None,
        compiled_contract: Optional[str] = None,
        constructor_args: Optional[Union[List, Dict]] = None,
        search_paths: Optional[List[str]] = None,
        deployer_address: int = 0,
    ) -> int:
        """
        Computes address for given contract.
        Either `compilation_source` or `compiled_contract` is required.

        :param salt: int
        :param compilation_source: string containing source code or a list of source files paths
        :param compiled_contract: string containing compiled contract. Useful for reading compiled contract from a file.
        :param constructor_args: a ``list`` or ``dict`` of arguments for the constructor.
        :param search_paths: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts.
        :param deployer_address: address of the deployer (if not provided default 0 is used)

        :raises: `ValueError` if neither compilation_source nor compiled_contract is provided.

        :return: contract's address
        """
        # pylint: disable=too-many-arguments
        warnings.warn(
            "Argument compilation_source is deprecated and will be removed in the future. "
            "Consider using already compiled contracts.",
            category=DeprecationWarning,
        )

        compiled = create_compiled_contract(
            compilation_source, compiled_contract, search_paths
        )
        translated_args = translate_constructor_args(compiled.abi, constructor_args)
        return compute_address(
            salt=salt,
            class_hash=compute_class_hash(compiled, hash_func=pedersen_hash),
            constructor_calldata=translated_args,
            deployer_address=deployer_address,
        )

    @staticmethod
    def compute_contract_hash(
        compilation_source: Optional[StarknetCompilationSource] = None,
        compiled_contract: Optional[str] = None,
        search_paths: Optional[List[str]] = None,
    ) -> int:
        """
        Computes hash for given contract.
        Either `compilation_source` or `compiled_contract` is required.

        :param compilation_source: string containing source code or a list of source files paths
        :param compiled_contract: string containing compiled contract. Useful for reading compiled contract from a file.
        :param search_paths: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts.
        :raises: `ValueError` if neither compilation_source nor compiled_contract is provided.
        :return:
        """
        warnings.warn(
            "Argument compilation_source is deprecated and will be removed in the future. "
            "Consider using already compiled contracts.",
            category=DeprecationWarning,
        )

        compiled_contract = create_compiled_contract(
            compilation_source, compiled_contract, search_paths
        )
        return compute_class_hash(compiled_contract, hash_func=pedersen_hash)

    @classmethod
    def _make_functions(
        cls, contract_data: ContractData, client: Client, account: Optional[BaseAccount]
    ) -> FunctionsRepository:
        repository = {}

        for abi_entry in contract_data.abi:
            if abi_entry["type"] != "function":
                continue

            name = abi_entry["name"]
            repository[name] = ContractFunction(
                name=name,
                abi=abi_entry,
                contract_data=contract_data,
                client=client,
                account=account,
            )

        return repository

    @staticmethod
    def _create_proxy_config(proxy_config) -> ProxyConfig:
        if proxy_config is False:
            return ProxyConfig()
        proxy_arg = ProxyConfig() if proxy_config is True else proxy_config
        return prepare_proxy_config(proxy_arg)


def _unpack_provider(
    provider: Union[BaseAccount, Client], client: Optional[Client] = None
) -> Tuple[Client, Optional[BaseAccount]]:
    """
    Get the client and optional account to be used by Contract.

    If provided with AccountClient, returns underlying Client and _AccountProxy.
    If provided with Client, returns this Client and None.
    If provided with Account, returns underlying Client and the account.
    """
    if client is not None:
        warnings.warn(
            "Argument client has been deprecated. Use provider instead.",
            category=DeprecationWarning,
        )

    if provider is not None and client is not None:
        raise ValueError("Arguments provider and client are mutually exclusive.")

    if provider is None and client is None:
        raise ValueError("One of provider or client must be provided.")

    provider = provider or client

    if isinstance(provider, Client):
        if isinstance(provider, AccountClient):
            return provider.client, AccountProxy(provider)

        return provider, None

    if isinstance(provider, BaseAccount):
        return provider.client, provider

    raise ValueError("Argument provider is not of accepted type.")


def _account_or_proxy(account: Union[BaseAccount, AccountClient]) -> BaseAccount:
    if isinstance(account, AccountClient):
        return AccountProxy(account)
    return account
