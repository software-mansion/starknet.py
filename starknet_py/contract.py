from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional, Tuple, TypeVar, Union

from marshmallow import ValidationError

from starknet_py.abi.v0 import Abi as AbiV0
from starknet_py.abi.v0 import AbiParser as AbiParserV0
from starknet_py.abi.v1 import Abi as AbiV1
from starknet_py.abi.v1 import AbiParser as AbiParserV1
from starknet_py.abi.v2 import Abi as AbiV2
from starknet_py.abi.v2 import AbiParser as AbiParserV2
from starknet_py.abi.v2.shape import (
    FUNCTION_ENTRY,
    IMPL_ENTRY,
    INTERFACE_ENTRY,
    L1_HANDLER_ENTRY,
)
from starknet_py.common import create_compiled_contract, create_sierra_compiled_contract
from starknet_py.constants import DEFAULT_DEPLOYER_ADDRESS
from starknet_py.contract_utils import _extract_compiled_class_hash, _unpack_provider
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client import Client
from starknet_py.net.client_models import (
    Call,
    EstimatedFee,
    Hash,
    ResourceBoundsMapping,
    Tag,
)
from starknet_py.net.models import AddressRepresentation, parse_address
from starknet_py.net.models.transaction import DeclareV3, InvokeV3
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.proxy.contract_abi_resolver import (
    ContractAbiResolver,
    ProxyConfig,
    prepare_proxy_config,
)
from starknet_py.serialization import TupleDataclass, serializer_for_function
from starknet_py.serialization.factory import serializer_for_function_v1
from starknet_py.serialization.function_serialization_adapter import (
    FunctionSerializationAdapterV0,
    FunctionSerializationAdapterV1,
)
from starknet_py.utils.constructor_args_translator import _is_abi_v2
from starknet_py.utils.sync import add_sync_methods

# pylint: disable=too-many-lines

ABI = list
ABIEntry = dict
TypeSentTransaction = TypeVar("TypeSentTransaction", bound="SentTransaction")


@dataclass(frozen=True)
class ContractData:
    """
    Basic data of a deployed contract.
    """

    address: int
    abi: ABI
    cairo_version: int

    @cached_property
    def parsed_abi(self) -> Union[AbiV0, AbiV1, AbiV2]:
        """
        Abi parsed into proper dataclass.

        :return: Abi
        """
        if self.cairo_version == 1:
            if _is_abi_v2(self.abi):
                return AbiParserV2(self.abi).parse()
            return AbiParserV1(self.abi).parse()
        return AbiParserV0(self.abi).parse()

    @staticmethod
    def from_abi(address: int, abi: ABI, cairo_version: int = 1) -> ContractData:
        """
        Create ContractData from ABI.

        :param address: Address of the deployed contract.
        :param abi: Abi of the contract.
        :param cairo_version: Version of the Cairo in which contract is written.
        :return: ContractData instance.
        """
        return ContractData(
            address=address,
            abi=abi,
            cairo_version=cairo_version,
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
        self: TypeSentTransaction,
        check_interval: float = 2,
        retries: int = 500,
    ) -> TypeSentTransaction:
        """
        Waits for transaction to be accepted on chain till ``ACCEPTED`` status.
        Returns a new SentTransaction instance, **does not mutate original instance**.
        """

        tx_receipt = await self._client.wait_for_tx(
            self.hash,
            check_interval=check_interval,
            retries=retries,
        )
        return dataclasses.replace(
            self,
            status=tx_receipt.finality_status,
            block_number=tx_receipt.block_number,
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

    invoke_transaction: InvokeV3 = None  # pyright: ignore
    """A InvokeTransaction instance used."""

    def __post_init__(self):
        assert self.contract is not None
        assert self.invoke_transaction is not None


@add_sync_methods
@dataclass(frozen=True)
class DeclareResult(SentTransaction):
    """
    Result of the Declare transaction.
    """

    _account: BaseAccount = None  # pyright: ignore
    _cairo_version: int = 1

    class_hash: int = None  # pyright: ignore
    """Class hash of the declared contract."""

    compiled_contract: str = None  # pyright: ignore
    """Compiled contract that was declared."""

    declare_transaction: DeclareV3 = None  # pyright: ignore
    """A Declare transaction that has been sent."""

    def __post_init__(self):
        if self._account is None:
            raise ValueError("Argument _account can't be None.")

        if self.class_hash is None:
            raise ValueError("Argument class_hash can't be None.")

        if self.compiled_contract is None:
            raise ValueError("Argument compiled_contract can't be None.")

        if self.declare_transaction is None:
            raise ValueError("Argument declare_transaction can't be None.")

    async def deploy_v3(
        self,
        *,
        deployer_address: AddressRepresentation = DEFAULT_DEPLOYER_ADDRESS,
        salt: Optional[int] = None,
        unique: bool = True,
        constructor_args: Optional[Union[List, Dict]] = None,
        nonce: Optional[int] = None,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        auto_estimate: bool = False,
        tip: int = 0,
    ) -> "DeployResult":
        """
        Deploys a contract.

        :param deployer_address: Address of the UDC. Is set to the address of
            the default UDC (same address on mainnet/sepolia) by default.
            Must be set when using custom network other than ones listed above.
        :param salt: Optional salt. Random value is selected if it is not provided.
        :param unique: Determines if the contract should be salted with the account address.
        :param constructor_args: a ``list`` or ``dict`` of arguments for the constructor.
        :param nonce: Nonce of the transaction with call to deployer.
        :param resource_bounds: Resource limits (L1 and L2) used when executing this transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :param tip: The tip amount to be added to the transaction fee.
        :return: DeployResult instance.
        """
        # pylint: disable=too-many-arguments, too-many-locals
        abi = self._get_abi()

        return await Contract.deploy_contract_v3(
            account=self._account,
            class_hash=self.class_hash,
            abi=abi,
            constructor_args=constructor_args,
            deployer_address=deployer_address,
            cairo_version=self._cairo_version,
            nonce=nonce,
            resource_bounds=resource_bounds,
            auto_estimate=auto_estimate,
            salt=salt,
            unique=unique,
            tip=tip,
        )

    def _get_abi(self) -> List:
        if self._cairo_version == 0:
            abi = create_compiled_contract(compiled_contract=self.compiled_contract).abi
        else:
            try:
                sierra_compiled_contract = create_sierra_compiled_contract(
                    compiled_contract=self.compiled_contract
                )
                abi = sierra_compiled_contract.parsed_abi

            except Exception as exc:
                raise ValueError(
                    "Contract's ABI can't be converted to format List[Dict]. "
                    "Make sure provided compiled_contract is correct."
                ) from exc
        return abi


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


@dataclass
class PreparedCallBase(Call):
    _client: Client
    _payload_transformer: Union[
        FunctionSerializationAdapterV0, FunctionSerializationAdapterV1
    ]


@add_sync_methods
@dataclass
class PreparedFunctionCall(PreparedCallBase):
    """
    Prepared date to call a contract function.
    """

    async def call_raw(
        self,
        block_hash: Optional[str] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> List[int]:
        """
        Calls a method without translating the result into python values.

        :param block_hash: Optional block hash.
        :param block_number: Optional block number.
        :return: list of ints.
        """
        return await self._client.call_contract(
            call=self, block_hash=block_hash, block_number=block_number
        )

    async def call(
        self,
        block_hash: Optional[str] = None,
        block_number: Optional[Union[int, Tag]] = None,
    ) -> Union[TupleDataclass, Tuple]:
        """
        Calls a method.

        :param block_hash: Optional block hash.
        :param block_number: Optional block number.
        :return: TupleDataclass representing call result.
        """
        result = await self.call_raw(block_hash=block_hash, block_number=block_number)
        return self._payload_transformer.deserialize(result)


@add_sync_methods
@dataclass
class PreparedFunctionInvoke(ABC, PreparedCallBase):
    _contract_data: ContractData
    _account: Optional[BaseAccount]

    def __post_init__(self):
        if self._account is None:
            raise ValueError(
                "Contract instance was created without providing an Account. "
                "It is not possible to prepare and send an invoke transaction."
            )

    @property
    def get_account(self):
        if self._account is not None:
            return self._account

        raise ValueError(
            "The account is not defined. It is not possible to send an invoke transaction."
        )

    @abstractmethod
    async def estimate_fee(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
        *,
        nonce: Optional[int] = None,
    ) -> EstimatedFee:
        """
        Estimate fee for prepared function call.

        :param block_hash: Estimate fee at specific block hash.
        :param block_number: Estimate fee at given block number
            (or "latest" / "pre_confirmed" for the latest / pre_confirmed block), default is "pre_confirmed".
        :param nonce: Nonce of the transaction.
        :return: Estimated amount of the transaction cost, either in Wei or Fri associated with executing the
            specified transaction.
        """

    async def _invoke(self, transaction: InvokeV3) -> InvokeResult:
        response = await self._client.send_transaction(transaction)

        invoke_result = InvokeResult(
            hash=response.transaction_hash,  # noinspection PyTypeChecker
            _client=self._client,
            contract=self._contract_data,
            invoke_transaction=transaction,
        )

        return invoke_result


@add_sync_methods
@dataclass
class PreparedFunctionInvokeV3(PreparedFunctionInvoke):
    """
    Prepared date to send an InvokeV3 transaction.
    """

    resource_bounds: Optional[ResourceBoundsMapping]
    tip: int = 0

    async def invoke(
        self,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        auto_estimate: bool = False,
        *,
        nonce: Optional[int] = None,
        tip: int = 0,
    ) -> InvokeResult:
        """
        Send an Invoke transaction version 3 for the prepared data.

        :param resource_bounds: Resource limits (L1 and L2) used when executing this transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :param nonce: Nonce of the transaction.
        :param tip: The tip amount to be added to the transaction fee.
        :return: InvokeResult.
        """

        transaction = await self.get_account.sign_invoke_v3(
            calls=self,
            nonce=nonce,
            resource_bounds=resource_bounds or self.resource_bounds,
            auto_estimate=auto_estimate,
            tip=tip or self.tip,
        )

        return await self._invoke(transaction)

    async def estimate_fee(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
        *,
        nonce: Optional[int] = None,
    ) -> EstimatedFee:
        tx = await self.get_account.sign_invoke_v3(
            calls=self,
            nonce=nonce,
            resource_bounds=ResourceBoundsMapping.init_with_zeros(),
        )
        estimate_tx = await self.get_account.sign_for_fee_estimate(transaction=tx)

        estimated_fee = await self._client.estimate_fee(
            tx=estimate_tx,
            block_hash=block_hash,
            block_number=block_number,
        )

        assert isinstance(estimated_fee, EstimatedFee)
        return estimated_fee


@add_sync_methods
class ContractFunction:
    def __init__(
        self,
        name: str,
        abi: ABIEntry,
        contract_data: ContractData,
        client: Client,
        account: Optional[BaseAccount],
        cairo_version: int = 1,
        *,
        interface_name: Optional[str] = None,
    ):
        # pylint: disable=too-many-arguments
        self.name = name
        self.abi = abi
        self.inputs = abi["inputs"]
        self.contract_data = contract_data
        self.client = client
        self.account = account

        if abi["type"] == L1_HANDLER_ENTRY:
            assert not isinstance(contract_data.parsed_abi, AbiV1)
            function = (
                contract_data.parsed_abi.l1_handler
                if contract_data.parsed_abi.l1_handler is None
                or isinstance(contract_data.parsed_abi.l1_handler, AbiV0.Function)
                else contract_data.parsed_abi.l1_handler.get(name)
            )
        elif interface_name is None:
            function = contract_data.parsed_abi.functions.get(name)
        else:
            assert isinstance(contract_data.parsed_abi, AbiV2)
            interface = contract_data.parsed_abi.interfaces[interface_name]
            function = interface.items[name]

        assert function is not None

        if cairo_version == 1:
            assert not isinstance(function, AbiV0.Function) and function is not None
            self._payload_transformer = serializer_for_function_v1(function)

        else:
            assert isinstance(function, AbiV0.Function) and function is not None
            self._payload_transformer = serializer_for_function(function)

    def prepare_call(
        self,
        *args,
        **kwargs,
    ) -> PreparedFunctionCall:
        """
        ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        Creates a ``PreparedFunctionCall`` instance which exposes calldata for every argument
        and adds more arguments when calling methods.

        :return: PreparedFunctionCall.
        """

        calldata = self._payload_transformer.serialize(*args, **kwargs)
        return PreparedFunctionCall(
            to_addr=self.contract_data.address,
            calldata=calldata,
            selector=self.get_selector(self.name),
            _client=self.client,
            _payload_transformer=self._payload_transformer,
        )

    async def call(
        self,
        *args,
        block_hash: Optional[str] = None,
        block_number: Optional[Union[int, Tag]] = None,
        **kwargs,
    ) -> Union[TupleDataclass, Tuple]:
        """
        Call contract's function. ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        The result is translated from Cairo data to python values.
        Equivalent of ``.prepare_call(*args, **kwargs).call()``.

        :param block_hash: Block hash to perform the call to the contract at specific point of time.
        :param block_number: Block number to perform the call to the contract at specific point of time.
        :return: TupleDataclass representing call result.
        """
        return await self.prepare_call(*args, **kwargs).call(
            block_hash=block_hash, block_number=block_number
        )

    def prepare_invoke_v3(
        self,
        *args,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        tip: int = 0,
        **kwargs,
    ) -> PreparedFunctionInvokeV3:
        """
        ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        Creates a ``PreparedFunctionInvokeV3`` instance which exposes calldata for every argument
        and adds more arguments when calling methods.

        :param resource_bounds: Resource limits (L1 and L2) used when executing this transaction.
        :return: PreparedFunctionInvokeV3.
        """

        calldata = self._payload_transformer.serialize(*args, **kwargs)
        return PreparedFunctionInvokeV3(
            to_addr=self.contract_data.address,
            calldata=calldata,
            selector=self.get_selector(self.name),
            resource_bounds=resource_bounds,
            tip=tip,
            _contract_data=self.contract_data,
            _client=self.client,
            _account=self.account,
            _payload_transformer=self._payload_transformer,
        )

    async def invoke_v3(
        self,
        *args,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        auto_estimate: bool = False,
        nonce: Optional[int] = None,
        **kwargs,
    ) -> InvokeResult:
        """
        Invoke contract's function. ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        Equivalent of ``.prepare_invoke_v3(*args, **kwargs).invoke()``.

        :param resource_bounds: Resource limits (L1 and L2) used when executing this transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :param nonce: Nonce of the transaction.
        :return: InvokeResult.
        """
        prepared_invoke = self.prepare_invoke_v3(*args, **kwargs)
        return await prepared_invoke.invoke(
            resource_bounds=resource_bounds,
            nonce=nonce,
            auto_estimate=auto_estimate,
        )

    @staticmethod
    def get_selector(function_name: str):
        """
        :param function_name: Contract function's name.
        :return: A Starknet integer selector for this function inside the contract.
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
        provider: Union[BaseAccount, Client],
        *,
        cairo_version: int = 1,
    ):
        """
        Should be used instead of ``from_address`` when ABI is known statically.

        Arguments provider and client are mutually exclusive and cannot be provided at the same time.

        :param address: contract's address.
        :param abi: contract's abi.
        :param provider: BaseAccount or Client used to perform transactions.
        :param cairo_version: Version of the Cairo in which contract is written.
        """
        client, account = _unpack_provider(provider)

        self.account: Optional[BaseAccount] = account
        self.client: Client = client
        self.data = ContractData.from_abi(parse_address(address), abi, cairo_version)

        try:
            self._functions = self._make_functions(
                contract_data=self.data,
                client=self.client,
                account=self.account,
                cairo_version=cairo_version,
            )
        except ValidationError as exc:
            raise ValueError(
                "Make sure valid ABI is used to create a Contract instance"
            ) from exc

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
            :class:`starknet_py.proxy.proxy_check.OpenZeppelinProxyCheck` and
            :class:`starknet_py.proxy.proxy_check.ArgentProxyCheck`.

            If set to ``False``, :meth:`Contract.from_address` will not resolve proxies.

            If a valid :class:`starknet_py.contract_abi_resolver.ProxyConfig` is provided, will use its values instead.

        :return: an initialized Contract instance.
        """
        client, account = _unpack_provider(provider)

        address = parse_address(address)
        proxy_config = Contract._create_proxy_config(proxy_config)

        abi, cairo_version = await ContractAbiResolver(
            address=address, client=client, proxy_config=proxy_config
        ).resolve()

        return Contract(
            address=address,
            abi=abi,
            provider=account or client,
            cairo_version=cairo_version,
        )

    @staticmethod
    async def declare_v3(
        account: BaseAccount,
        compiled_contract: str,
        *,
        compiled_contract_casm: Optional[str] = None,
        compiled_class_hash: Optional[int] = None,
        nonce: Optional[int] = None,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        auto_estimate: bool = False,
        tip: int = 0,
    ) -> DeclareResult:
        # pylint: disable=too-many-arguments

        """
        Declares a contract.

        :param account: BaseAccount used to sign and send declare transaction.
        :param compiled_contract: String containing compiled contract.
        :param compiled_contract_casm: String containing the content of the starknet-sierra-compile (.casm file).
        :param compiled_class_hash: Hash of the compiled_contract_casm.
        :param nonce: Nonce of the transaction.
        :param resource_bounds: Resource limits (L1 and L2) used when executing this transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :param tip: The tip amount to be added to the transaction fee.
        :return: DeclareResult instance.
        """

        compiled_class_hash = _extract_compiled_class_hash(
            compiled_contract_casm, compiled_class_hash
        )

        declare_tx = await account.sign_declare_v3(
            compiled_contract=compiled_contract,
            compiled_class_hash=compiled_class_hash,
            nonce=nonce,
            resource_bounds=resource_bounds,
            auto_estimate=auto_estimate,
            tip=tip,
        )

        return await _declare_contract(
            declare_tx, account, compiled_contract, cairo_version=1
        )

    @staticmethod
    async def deploy_contract_v3(
        account: BaseAccount,
        class_hash: Hash,
        abi: Optional[List] = None,
        constructor_args: Optional[Union[List, Dict]] = None,
        *,
        deployer_address: AddressRepresentation = DEFAULT_DEPLOYER_ADDRESS,
        cairo_version: int = 1,
        nonce: Optional[int] = None,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
        auto_estimate: bool = False,
        salt: Optional[int] = None,
        unique: bool = True,
        tip: int = 0,
    ) -> "DeployResult":
        """
        Deploys a contract through Universal Deployer Contract.

        :param account: BaseAccount used to sign and send deploy transaction.
        :param class_hash: The class_hash of the contract to be deployed.
        :param abi: An abi of the contract to be deployed.
        :param constructor_args: a ``list`` or ``dict`` of arguments for the constructor.
        :param deployer_address: Address of the UDC. Is set to the address of
            the default UDC (same address on mainnet/sepolia) by default.
            Must be set when using custom network other than ones listed above.
        :param cairo_version: Version of the Cairo in which contract is written.
            By default, it is set to 1.
        :param nonce: Nonce of the transaction.
        :param resource_bounds: Resource limits (L1 and L2) used when executing this transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :param salt: Optional salt. Random value is selected if it is not provided.
        :param unique: Determines if the contract should be salted with the account address.
        :param tip: The tip amount to be added to the transaction fee.
        :return: DeployResult instance.
        """
        # pylint: disable=too-many-arguments, too-many-locals
        deployer = Deployer(
            deployer_address=deployer_address,
            account_address=account.address if unique else None,
        )
        deploy_call, address = deployer.create_contract_deployment(
            class_hash=class_hash,
            salt=salt,
            abi=abi,
            calldata=constructor_args,
            cairo_version=cairo_version,
        )

        res = await account.execute_v3(
            calls=deploy_call,
            nonce=nonce,
            resource_bounds=resource_bounds,
            auto_estimate=auto_estimate,
            tip=tip,
        )

        if abi is None:
            contract_class = await account.client.get_class_by_hash(class_hash)
            abi = ContractAbiResolver.get_abi_from_contract_class(contract_class)

        deployed_contract = Contract(
            provider=account, address=address, abi=abi, cairo_version=cairo_version
        )

        deploy_result = DeployResult(
            hash=res.transaction_hash,
            _client=account.client,
            deployed_contract=deployed_contract,
        )

        return deploy_result

    @classmethod
    def _make_functions(
        cls,
        contract_data: ContractData,
        client: Client,
        account: Optional[BaseAccount],
        cairo_version: int = 1,
    ) -> FunctionsRepository:
        repository = {}
        implemented_interfaces = [
            entry["interface_name"]
            for entry in contract_data.abi
            if entry["type"] == IMPL_ENTRY
        ]

        for abi_entry in contract_data.abi:
            if abi_entry["type"] in [FUNCTION_ENTRY, L1_HANDLER_ENTRY]:
                name = abi_entry["name"]
                repository[name] = ContractFunction(
                    name=name,
                    abi=abi_entry,
                    contract_data=contract_data,
                    client=client,
                    account=account,
                    cairo_version=cairo_version,
                )

            if (
                abi_entry["type"] == INTERFACE_ENTRY
                and abi_entry["name"] in implemented_interfaces
            ):
                for item in abi_entry["items"]:
                    name = item["name"]
                    repository[name] = ContractFunction(
                        name=name,
                        abi=item,
                        contract_data=contract_data,
                        client=client,
                        account=account,
                        cairo_version=cairo_version,
                        interface_name=abi_entry["name"],
                    )

        return repository

    @staticmethod
    def _create_proxy_config(proxy_config) -> ProxyConfig:
        if proxy_config is False:
            return ProxyConfig()
        proxy_arg = ProxyConfig() if proxy_config is True else proxy_config
        return prepare_proxy_config(proxy_arg)


async def _declare_contract(
    transaction: DeclareV3,
    account: BaseAccount,
    compiled_contract: str,
    cairo_version: int,
) -> DeclareResult:
    res = await account.client.declare(transaction=transaction)

    return DeclareResult(
        hash=res.transaction_hash,
        class_hash=res.class_hash,
        compiled_contract=compiled_contract,
        declare_transaction=transaction,
        _account=account,
        _client=account.client,
        _cairo_version=cairo_version,
    )
