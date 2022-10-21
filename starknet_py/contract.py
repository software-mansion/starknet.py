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
    Any,
)
from typing import TypedDict

from starkware.cairo.lang.compiler.identifier_manager import IdentifierManager
from starkware.starknet.core.os.class_hash import compute_class_hash
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    CastableToHash,
)

from starknet_py.common import create_compiled_contract
from starknet_py.compile.compiler import StarknetCompilationSource
from starknet_py.net import AccountClient
from starknet_py.net.client import Client
from starknet_py.net.client_models import Hash, Tag
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import (
    InvokeFunction,
    AddressRepresentation,
    parse_address,
    compute_address,
)
from starknet_py.proxy_check import ProxyCheck, ArgentProxyCheck, OpenZeppelinProxyCheck
from starknet_py.transactions.deploy import make_deploy_tx
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
class DeployResult(SentTransaction):
    # We ensure this is not None in __post_init__
    deployed_contract: "Contract" = None  # pyright: ignore

    def __post_init__(self):
        assert self.deployed_contract is not None


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
        return await self._client.call_contract(invoke_tx=self, block_hash=block_hash)

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

    class ProxyConfig(TypedDict, total=False):
        """
        Proxy resolving configuration
        """

        max_steps: int
        """
        Max number of contracts that `Contract.from_address` will process before raising `RecursionError`.
        """
        proxy_checks: List[ProxyCheck]
        """
        List of classes implementing :class:`starknet_py.proxy_check.ProxyCheck` ABC,
        that will be used for checking if contract at the address is a proxy contract.
        """

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
        :raises TypeError: when Client not supporting `get_code` methods is used
        :param address: Contract's address
        :param client: Client
        :param proxy_config: Proxy resolving config
            If set to ``True``, will use default proxy checks and :class:
            `starknet_py.proxy_check.OpenZeppelinProxyCheck`
            and :class:`starknet_py.proxy_check.ArgentProxyCheck` and default max_steps = 5.

            If set to ``False``, :meth:`Contract.from_address` will not resolve proxies.

            If a valid `ProxyConfig` is provided, will use values from that instead supplementing
            with defaults when needed.

        :return: an initialized Contract instance
        """
        default_config: Contract.ProxyConfig = {
            "max_steps": 5,
            "proxy_checks": [ArgentProxyCheck(), OpenZeppelinProxyCheck()],
        }
        if isinstance(proxy_config, bool):
            proxy_config = default_config if proxy_config else {}
        else:
            proxy_config = {**default_config, **proxy_config}

        proxy_client = client.client if isinstance(client, AccountClient) else client
        if not isinstance(proxy_client, GatewayClient):
            raise TypeError(
                "Contract.from_address only supports GatewayClient or AccountClients using GatewayClient"
            )

        contract = await ContractFromAddressFactory(
            address=address,
            client=proxy_client,
            max_steps=proxy_config.get("max_steps", 1),
            proxy_checks=proxy_config.get("proxy_checks", []),
        ).make_contract()

        return Contract(address=address, abi=contract.data.abi, client=client)

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
            This metodh has been deprecated in favor of deploying through cairo syscall.
        """
        warnings.warn(
            "In the future versions of StarkNet, Deploy transaction will not be supported."
            "To deploy a contract use cairo syscall",
            category=DeprecationWarning,
        )

        compiled = create_compiled_contract(
            compilation_source, compiled_contract, search_paths
        )
        translated_args = Contract._translate_constructor_args(
            compiled, constructor_args
        )
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
        compiled_contract = create_compiled_contract(
            compilation_source, compiled_contract, search_paths
        )
        translated_args = Contract._translate_constructor_args(
            compiled_contract, constructor_args
        )
        return compute_address(
            salt=salt,
            class_hash=compute_class_hash(compiled_contract, hash_func=pedersen_hash),
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

    @staticmethod
    def _translate_constructor_args(
        contract: ContractClass, constructor_args: Any
    ) -> List[int]:
        constructor_abi = next(
            (member for member in contract.abi if member["type"] == "constructor"),
            None,
        )

        # Constructor might not accept any arguments
        if not constructor_abi or not constructor_abi["inputs"]:
            return []

        if not constructor_args:
            raise ValueError(
                "Provided contract has a constructor and no args were provided."
            )

        args, kwargs = (
            ([], constructor_args)
            if isinstance(constructor_args, dict)
            else (constructor_args, {})
        )
        calldata, _args = FunctionCallSerializer(
            constructor_abi, identifier_manager_from_abi(contract.abi)
        ).from_python(*args, **kwargs)
        return calldata

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


class ContractFromAddressFactory:
    def __init__(
        self,
        address: AddressRepresentation,
        client: GatewayClient,
        max_steps: int,
        proxy_checks: List[ProxyCheck],
    ):
        self._address = address
        self._client = client
        self._max_steps = max_steps
        self._proxy_checks = proxy_checks
        self._processed_addresses = set()

    async def make_contract(self) -> Contract:
        return await self._make_contract_recursively(step=1, address=self._address)

    async def _make_contract_recursively(
        self, step: int, address: AddressRepresentation
    ) -> Contract:
        if address in self._processed_addresses:
            raise RecursionError("Proxy cycle detected while resolving proxies")

        if step > self._max_steps:
            raise RecursionError("Max number of steps exceeded while resolving proxies")

        code = await self._client.get_code(contract_address=parse_address(address))
        contract = Contract(
            address=parse_address(address), abi=code.abi, client=self._client
        )
        self._processed_addresses.add(address)

        is_proxy = False
        address = 0
        for proxy_check in self._proxy_checks:
            if await proxy_check.is_proxy(contract):
                is_proxy = True
                address = await proxy_check.implementation_address(contract)
                break

        if not is_proxy:
            return contract

        return await self._make_contract_recursively(
            address=address,
            step=step + 1,
        )
