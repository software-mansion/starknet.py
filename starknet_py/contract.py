from __future__ import annotations

import dataclasses
import warnings
from dataclasses import dataclass
from typing import (
    List,
    Optional,
    TypeVar,
    Union,
    Dict,
    NamedTuple,
)

from starkware.cairo.lang.compiler.identifier_manager import IdentifierManager
from starkware.starknet.core.os.class_hash import compute_class_hash
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    CastableToHash,
)

from starknet_py.common import create_compiled_contract
from starknet_py.compile.compiler import StarknetCompilationSource
from starknet_py.constants import DEFAULT_DEPLOYER_ADDRESS
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.proxy.contract_abi_resolver import (
    ProxyConfig,
    ContractAbiResolver,
    prepare_proxy_config,
)
from starknet_py.net import AccountClient
from starknet_py.net.client import Client
from starknet_py.net.client_models import Hash, Tag
from starknet_py.net.models import (
    InvokeFunction,
    AddressRepresentation,
    parse_address,
    compute_address,
)
from starknet_py.transactions.deploy import make_deploy_tx
from starknet_py.utils.contructor_args_translator import translate_constructor_args
from starknet_py.utils.crypto.facade import pedersen_hash, Call
from starknet_py.utils.data_transformer import FunctionCallSerializer
from starknet_py.utils.sync import add_sync_methods

ABI = list
ABIEntry = dict
TSentTransaction = TypeVar("TSentTransaction", bound="SentTransaction")


@dataclass(frozen=True)
class ContractData:
    address: int
    abi: ABI
    identifier_manager: IdentifierManager

    @staticmethod
    def from_abi(address: int, abi: ABI) -> "ContractData":
        return ContractData(
            address=address,
            abi=abi,
            identifier_manager=identifier_manager_from_abi(abi),
        )


@add_sync_methods
@dataclass(frozen=True)
class SentTransaction:
    """
    Dataclass exposing the interface of transaction related to a performed action
    """

    hash: CastableToHash
    _client: Client
    status: Optional[str] = None
    block_number: Optional[int] = None

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
    # We ensure these are not None in __post_init__
    contract: ContractData = None  # pyright: ignore
    invoke_transaction: InvokeFunction = None  # pyright: ignore

    def __post_init__(self):
        assert self.contract is not None
        assert self.invoke_transaction is not None


InvocationResult = InvokeResult


@add_sync_methods
@dataclass(frozen=True)
class DeclareResult(SentTransaction):
    _account: AccountClient = None  # pyright: ignore
    class_hash: int = None  # pyright: ignore
    compiled_contract: str = None  # pyright: ignore

    def __post_init__(self):
        if any(
            field is None
            for field in [self.class_hash, self._account, self.compiled_contract]
        ):
            raise ValueError(
                "None of the account, class_hash and compiled_contract fields can be None"
            )

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
        Deploys a contract

        :param deployer_address: Address of the UDC. Is set to the address of
            the default UDC (same address on mainnet/testnet/devnet) by default.
            Must be set when using custom network other than ones listed above.
        :param salt: Optional salt. Random value is selected if it is not provided.
        :param unique: Determines if the contract should be salted with the account address.
        :param constructor_args: a ``list`` or ``dict`` of arguments for the constructor.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :return: DeployResult instance
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
            client=self._account,
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
    # We ensure this is not None in __post_init__
    deployed_contract: "Contract" = None  # pyright: ignore

    def __post_init__(self):
        if self.deployed_contract is None:
            raise ValueError("deployed_contract can't be None")


# pylint: disable=too-many-instance-attributes
@add_sync_methods
class PreparedFunctionCall(Call):
    def __init__(
        self,
        calldata: List[int],
        arguments: Dict[str, List[int]],
        selector: int,
        client: Client,
        payload_transformer: FunctionCallSerializer,
        contract_data: ContractData,
        max_fee: Optional[int],
        version: int,
    ):
        # pylint: disable=too-many-arguments
        super().__init__(
            to_addr=contract_data.address, selector=selector, calldata=calldata
        )
        self.arguments = arguments
        self._client = client
        self._payload_transformer = payload_transformer
        self._contract_data = contract_data
        self.max_fee = max_fee
        self.version = version

    async def call_raw(
        self,
        block_hash: Optional[str] = None,
    ) -> List[int]:
        """
        Calls a method without translating the result into python values.

        :param block_hash: Optional block hash
        :return: list of ints
        """
        return await self._client.call_contract(call=self, block_hash=block_hash)

    async def call(
        self,
        block_hash: Optional[str] = None,
    ) -> NamedTuple:
        """
        Calls a method.

        :param block_hash: Optional block hash
        :return: CallResult or List[int] if return_raw is used
        """
        result = await self.call_raw(block_hash=block_hash)
        return self._payload_transformer.to_python(result)

    async def invoke(
        self,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> InvokeResult:
        """
        Invokes a method.

        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :return: InvokeResult
        """
        if max_fee is not None:
            self.max_fee = max_fee

        transaction = await self._account_client.sign_invoke_transaction(
            calls=self,
            max_fee=self.max_fee,
            auto_estimate=auto_estimate,
            version=self.version,
        )
        response = await self._account_client.send_transaction(transaction)

        invoke_result = InvokeResult(
            hash=response.transaction_hash,  # noinspection PyTypeChecker
            _client=self._account_client,
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
        Estimate fee for prepared function call

        :param block_hash: Estimate fee at specific block hash
        :param block_number: Estimate fee at given block number (or "pending" for pending block), default is "pending"
        :return: Estimated amount of Wei executing specified transaction will cost
        :raises ValueError: when max_fee of PreparedFunctionCall is not None or 0.
        """
        if self.max_fee is not None and self.max_fee != 0:
            raise ValueError(
                "Cannot estimate fee of PreparedFunctionCall with max_fee not None or 0."
            )

        tx = await self._account_client.sign_invoke_transaction(
            calls=self, max_fee=0, version=self.version
        )

        return await self._account_client.estimate_fee(
            tx=tx, block_hash=block_hash, block_number=block_number
        )

    @property
    def _account_client(self) -> AccountClient:
        client = self._client
        if isinstance(client, AccountClient):
            return client

        raise ValueError(
            "Contract uses an account that can't invoke transactions. You need to use AccountClient for that."
        )


@add_sync_methods
class ContractFunction:
    def __init__(
        self, name: str, abi: ABIEntry, contract_data: ContractData, client: Client
    ):
        self.name = name
        self.abi = abi
        self.inputs = abi["inputs"]
        self.contract_data = contract_data
        self._client = client
        self._payload_transformer = FunctionCallSerializer(
            abi=self.abi, identifier_manager=self.contract_data.identifier_manager
        )

    def prepare(
        self,
        *args,
        version: Optional[int] = None,
        max_fee: Optional[int] = None,
        **kwargs,
    ) -> PreparedFunctionCall:
        """
        ``*args`` and ``**kwargs`` are translated into Cairo calldata.
         Creates a ``PreparedFunctionCall`` instance
         which exposes calldata for every argument and adds more arguments when calling methods.

        :param version: PreparedFunctionCall version
        :param max_fee: Max amount of Wei to be paid when executing transaction
        :return: PreparedFunctionCall
        """
        if version is None:
            version = (
                self._client.supported_tx_version
                if isinstance(self._client, AccountClient)
                else 0
            )

        if version == 0:
            warnings.warn(
                "Transaction with version 0 is deprecated and will be removed in the future. "
                "Use AccountClient supporting the transaction version 1",
                category=DeprecationWarning,
            )

        calldata, arguments = self._payload_transformer.from_python(*args, **kwargs)
        return PreparedFunctionCall(
            calldata=calldata,
            arguments=arguments,
            contract_data=self.contract_data,
            client=self._client,
            payload_transformer=self._payload_transformer,
            selector=self.get_selector(self.name),
            max_fee=max_fee,
            version=version,
        )

    async def call(
        self,
        *args,
        block_hash: Optional[str] = None,
        version: Optional[int] = None,
        **kwargs,
    ) -> NamedTuple:
        """
        :param block_hash: Block hash to execute the contract at specific point of time
        :param version: Call version

        Call contract's function. ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        The result is translated from Cairo data to python values.
        Equivalent of ``.prepare(*args, **kwargs).call()``.
        """
        return await self.prepare(max_fee=0, version=version, *args, **kwargs).call(
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

        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        """
        prepared_call = self.prepare(*args, **kwargs)
        return await prepared_call.invoke(max_fee=max_fee, auto_estimate=auto_estimate)

    @staticmethod
    def get_selector(function_name: str):
        """
        :param function_name: Contract function's name
        :return: A StarkNet integer selector for this function inside the contract
        """
        return get_selector_from_name(function_name)


FunctionsRepository = Dict[str, ContractFunction]


@add_sync_methods
class Contract:
    """
    Cairo contract's model.
    """

    def __init__(self, address: AddressRepresentation, abi: list, client: Client):
        """
        Should be used instead of ``from_address`` when ABI is known statically.

        :param address: contract's address
        :param abi: contract's abi
        :param client: client used for API calls
        """
        self.data = ContractData.from_abi(parse_address(address), abi)
        self._functions = self._make_functions(self.data, client)
        self.client = client

    @property
    def functions(self) -> FunctionsRepository:
        """
        :return: All functions exposed from a contract.
        """
        return self._functions

    @property
    def address(self) -> int:
        return self.data.address

    @staticmethod
    async def from_address(
        address: AddressRepresentation,
        client: Client,
        proxy_config: Union[bool, ProxyConfig] = False,
    ) -> "Contract":
        """
        Fetches ABI for given contract and creates a new Contract instance with it. If you know ABI statically you
        should create Contract's instances directly instead of using this function to avoid unnecessary API calls.

        :raises ContractNotFoundError: when contract is not found
        :raises TypeError: when given client's `get_class_by_hash` method does not return abi
        :raises ProxyResolutionError: when given ProxyChecks were not sufficient to resolve proxy's implementation
        :param address: Contract's address
        :param client: Client
        :param proxy_config: Proxy resolving config
            If set to ``True``, will use default proxy checks
            :class:`starknet_py.proxy.proxy_check.OpenZeppelinProxyCheck`
            and :class:`starknet_py.proxy.proxy_check.ArgentProxyCheck`.

            If set to ``False``, :meth:`Contract.from_address` will not resolve proxies.

            If a valid :class:`starknet_py.contract_abi_resolver.ProxyConfig` is provided, will use its values instead.

        :return: an initialized Contract instance
        """
        address = parse_address(address)
        proxy_config = Contract._create_proxy_config(proxy_config)

        abi = await ContractAbiResolver(
            address=address, client=client, proxy_config=proxy_config
        ).resolve()

        return Contract(address=address, abi=abi, client=client)

    @staticmethod
    async def declare(
        account: AccountClient,
        compiled_contract: str,
        *,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeclareResult:
        """
        Declares a contract

        :param account: An AccountClient used to sign and send declare transaction.
        :param compiled_contract: String containing compiled contract.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :return: DeclareResult instance
        """
        declare_tx = await account.sign_declare_transaction(
            compiled_contract=compiled_contract,
            max_fee=max_fee,
            auto_estimate=auto_estimate,
        )
        res = await account.declare(transaction=declare_tx)

        return DeclareResult(
            hash=res.transaction_hash,
            _client=account.client,
            class_hash=res.class_hash,
            _account=account,
            compiled_contract=compiled_contract,
        )

    @staticmethod
    async def deploy_contract(
        account: AccountClient,
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
        :return: DeployResult instance
        """
        # pylint: disable=too-many-arguments
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
            client=account,
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
    async def deploy(
        client: Client,
        compilation_source: Optional[StarknetCompilationSource] = None,
        compiled_contract: Optional[str] = None,
        constructor_args: Optional[Union[List, Dict]] = None,
        salt: Optional[int] = None,
        search_paths: Optional[List[str]] = None,
    ) -> "DeployResult":
        # pylint: disable=too-many-arguments
        """
        Deploys a contract and waits until it has ``PENDING`` status.
        Either `compilation_source` or `compiled_contract` is required.

        :param client: Client
        :param compilation_source: string containing source code or a list of source files paths
        :param compiled_contract: string containing compiled contract. Useful for reading compiled contract from a file.
        :param constructor_args: a ``list`` or ``dict`` of arguments for the constructor.
        :param salt: Optional salt. Random value is selected if it is not provided.
        :param search_paths: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts.
        :raises: `ValueError` if neither compilation_source nor compiled_contract is provided.
        :return: DeployResult instance

        .. deprecated:: 0.8.0
            This method has been deprecated in favor of deploying through cairo syscall.
            To deploy a contract use `Contract.deploy_contract`.
        """
        warnings.warn(
            "In the future versions of StarkNet, Deploy transaction will not be supported."
            "To deploy a contract use cairo syscall",
            category=DeprecationWarning,
        )

        compiled = create_compiled_contract(
            compilation_source, compiled_contract, search_paths
        )
        translated_args = translate_constructor_args(compiled.abi, constructor_args)
        deploy_tx = make_deploy_tx(
            compiled_contract=compiled,
            constructor_calldata=translated_args,
            salt=salt,
        )
        res = await client.deploy(deploy_tx)
        contract_address = res.contract_address

        deployed_contract = Contract(
            client=client,
            address=contract_address,
            abi=compiled.abi,
        )
        deploy_result = DeployResult(
            hash=res.transaction_hash,
            _client=client,
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
        compiled_contract = create_compiled_contract(
            compilation_source, compiled_contract, search_paths
        )
        return compute_class_hash(compiled_contract, hash_func=pedersen_hash)

    @classmethod
    def _make_functions(
        cls, contract_data: ContractData, client: Client
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
            )

        return repository

    @staticmethod
    def _create_proxy_config(proxy_config) -> ProxyConfig:
        if proxy_config is False:
            return ProxyConfig()
        proxy_arg = ProxyConfig() if proxy_config is True else proxy_config
        return prepare_proxy_config(proxy_arg)
