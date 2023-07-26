from __future__ import annotations

import dataclasses
import json
import warnings
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional, Tuple, TypeVar, Union

from marshmallow import ValidationError

from starknet_py.abi.model import Abi
from starknet_py.abi.parser import AbiParser
from starknet_py.abi.v1.model import Abi as AbiV1
from starknet_py.abi.v1.parser import AbiParser as AbiV1Parser
from starknet_py.abi.v2.model import Abi as AbiV2
from starknet_py.abi.v2.parser import AbiParser as AbiV2Parser
from starknet_py.abi.v2.shape import (
    FUNCTION_ENTRY,
    IMPL_ENTRY,
    INTERFACE_ENTRY,
    L1_HANDLER_ENTRY,
)
from starknet_py.common import (
    create_casm_class,
    create_compiled_contract,
    create_sierra_compiled_contract,
)
from starknet_py.constants import DEFAULT_DEPLOYER_ADDRESS
from starknet_py.hash.address import compute_address
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.hash.class_hash import compute_class_hash
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client import Client
from starknet_py.net.client_models import Call, EstimatedFee, Hash, Tag
from starknet_py.net.models import AddressRepresentation, Invoke, parse_address
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.proxy.contract_abi_resolver import (
    ContractAbiResolver,
    ProxyConfig,
    prepare_proxy_config,
)
from starknet_py.serialization import TupleDataclass, serializer_for_function
from starknet_py.serialization.factory import serializer_for_function_v1
from starknet_py.serialization.function_serialization_adapter import (
    FunctionSerializationAdapter,
)
from starknet_py.utils.contructor_args_translator import (
    _is_abi_v2,
    translate_constructor_args,
)
from starknet_py.utils.sync import add_sync_methods

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
    def parsed_abi(self) -> Union[Abi, AbiV1, AbiV2]:
        """
        Abi parsed into proper dataclass.

        :return: Abi
        """
        if self.cairo_version == 1:
            if _is_abi_v2(self.abi):
                return AbiV2Parser(self.abi).parse()
            return AbiV1Parser(self.abi).parse()
        return AbiParser(self.abi).parse()

    @staticmethod
    def from_abi(address: int, abi: ABI, cairo_version: int = 0) -> ContractData:
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
        wait_for_accept: Optional[bool] = None,
        check_interval: float = 2,
        retries: int = 500,
    ) -> TypeSentTransaction:
        """
        Waits for transaction to be accepted on chain till ``ACCEPTED`` status.
        Returns a new SentTransaction instance, **does not mutate original instance**.
        """
        if wait_for_accept is not None:
            warnings.warn(
                "Parameter `wait_for_accept` has been deprecated - since Starknet 0.12.0, transactions in a PENDING"
                " block have status ACCEPTED_ON_L2."
            )

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
    _cairo_version: int = 0

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
        nonce: Optional[int] = None,
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
        :param nonce: Nonce of the transaction with call to deployer.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :return: DeployResult instance.
        """
        # pylint: disable=too-many-arguments, too-many-locals
        if self._cairo_version == 0:
            abi = create_compiled_contract(compiled_contract=self.compiled_contract).abi
        else:
            try:
                sierra_compiled_contract = create_sierra_compiled_contract(
                    compiled_contract=self.compiled_contract
                )
                abi = json.loads(sierra_compiled_contract.abi)
            except Exception as exc:
                raise ValueError(
                    "Contract's ABI can't be converted to format List[Dict]. "
                    "Make sure provided compiled_contract is correct."
                ) from exc

        deployer = Deployer(
            deployer_address=deployer_address,
            account_address=self._account.address if unique else None,
        )
        deploy_call, address = deployer.create_contract_deployment(
            class_hash=self.class_hash,
            salt=salt,
            abi=abi,
            calldata=constructor_args,
            cairo_version=self._cairo_version,
        )
        res = await self._account.execute(
            calls=deploy_call, nonce=nonce, max_fee=max_fee, auto_estimate=auto_estimate
        )

        deployed_contract = Contract(
            provider=self._account,
            address=address,
            abi=abi,
            cairo_version=self._cairo_version,
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

    @property
    def _account(self) -> BaseAccount:
        if self._internal_account is not None:
            return self._internal_account

        raise ValueError("Contract instance was created without providing an Account.")

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
    ) -> TupleDataclass:
        """
        Calls a method.

        :param block_hash: Optional block hash.
        :param block_number: Optional block number.
        :return: TupleDataclass representing call result.
        """
        result = await self.call_raw(block_hash=block_hash, block_number=block_number)
        return self._payload_transformer.deserialize(result)

    async def invoke(
        self,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        *,
        nonce: Optional[int] = None,
    ) -> InvokeResult:
        """
        Invokes a method.

        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :param nonce: Nonce of the transaction.
        :return: InvokeResult.
        """
        if max_fee is not None:
            self.max_fee = max_fee

        transaction = await self._account.sign_invoke_transaction(
            calls=self,
            nonce=nonce,
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
        *,
        nonce: Optional[int] = None,
    ) -> EstimatedFee:
        """
        Estimate fee for prepared function call.

        :param block_hash: Estimate fee at specific block hash.
        :param block_number: Estimate fee at given block number
            (or "latest" / "pending" for the latest / pending block), default is "pending".
        :param nonce: Nonce of the transaction.
        :return: Estimated amount of Wei executing specified transaction will cost.
        """
        tx = await self._account.sign_invoke_transaction(
            calls=self, nonce=nonce, max_fee=0
        )

        estimated_fee = await self._client.estimate_fee(
            tx=tx,
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
        cairo_version: int = 0,
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
            function = contract_data.parsed_abi.l1_handler
        elif interface_name is None:
            function = contract_data.parsed_abi.functions.get(name)
        else:
            assert isinstance(contract_data.parsed_abi, AbiV2)
            interface = contract_data.parsed_abi.interfaces[interface_name]
            function = interface.items[name]

        assert function is not None

        if cairo_version == 1:
            assert not isinstance(function, Abi.Function) and function is not None
            self._payload_transformer = serializer_for_function_v1(function)

        else:
            assert isinstance(function, Abi.Function) and function is not None
            self._payload_transformer = serializer_for_function(function)

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

        calldata = self._payload_transformer.serialize(*args, **kwargs)
        return PreparedFunctionCall(
            calldata=calldata,
            contract_data=self.contract_data,
            client=self.client,
            account=self.account,
            payload_transformer=self._payload_transformer,
            selector=self.get_selector(self.name),
            max_fee=max_fee,
        )

    async def call(
        self,
        *args,
        block_hash: Optional[str] = None,
        block_number: Optional[Union[int, Tag]] = None,
        **kwargs,
    ) -> TupleDataclass:
        """
        Call contract's function. ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        The result is translated from Cairo data to python values.
        Equivalent of ``.prepare(*args, **kwargs).call()``.

        :param block_hash: Block hash to perform the call to the contract at specific point of time.
        :param block_number: Block number to perform the call to the contract at specific point of time.
        """
        return await self.prepare(max_fee=0, *args, **kwargs).call(
            block_hash=block_hash, block_number=block_number
        )

    async def invoke(
        self,
        *args,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        nonce: Optional[int] = None,
        **kwargs,
    ) -> InvokeResult:
        """
        Invoke contract's function. ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        Equivalent of ``.prepare(*args, **kwargs).invoke()``.

        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :param nonce: Nonce of the transaction.
        """
        prepared_call = self.prepare(*args, **kwargs)
        return await prepared_call.invoke(
            max_fee=max_fee, nonce=nonce, auto_estimate=auto_estimate
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
        cairo_version: int = 0,
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
            :class:`starknet_py.proxy.proxy_check.OpenZeppelinProxyCheck`,
            :class:`starknet_py.proxy.proxy_check.ArgentProxyCheck`,
            and :class:`starknet_py.proxy.proxy_check.StarknetEthProxyCheck`.

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
    async def declare(
        account: BaseAccount,
        compiled_contract: str,
        *,
        compiled_contract_casm: Optional[str] = None,
        casm_class_hash: Optional[int] = None,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> DeclareResult:
        """
        Declares a contract.

        :param account: BaseAccount used to sign and send declare transaction.
        :param compiled_contract: String containing compiled contract.
        :param compiled_contract_casm: String containing the content of the starknet-sierra-compile (.casm file).
            Used when declaring Cairo1 contracts.
        :param casm_class_hash: Hash of the compiled_contract_casm.
        :param nonce: Nonce of the transaction.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :return: DeclareResult instance.
        """

        if Contract._get_cairo_version(compiled_contract) == 1:
            if casm_class_hash is None and compiled_contract_casm is None:
                raise ValueError(
                    "Cairo 1.0 contract was provided without casm_class_hash or compiled_contract_casm argument."
                )

            cairo_version = 1
            if casm_class_hash is None:
                assert compiled_contract_casm is not None
                casm_class_hash = compute_casm_class_hash(
                    create_casm_class(compiled_contract_casm)
                )

            declare_tx = await account.sign_declare_v2_transaction(
                compiled_contract=compiled_contract,
                compiled_class_hash=casm_class_hash,
                nonce=nonce,
                max_fee=max_fee,
                auto_estimate=auto_estimate,
            )
        else:
            cairo_version = 0
            declare_tx = await account.sign_declare_transaction(
                compiled_contract=compiled_contract,
                nonce=nonce,
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
            _cairo_version=cairo_version,
        )

    @staticmethod
    def _get_cairo_version(compiled_contract: str) -> int:
        return 1 if "sierra_program" in compiled_contract else 0

    @staticmethod
    async def deploy_contract(
        account: BaseAccount,
        class_hash: Hash,
        abi: List,
        constructor_args: Optional[Union[List, Dict]] = None,
        *,
        deployer_address: AddressRepresentation = DEFAULT_DEPLOYER_ADDRESS,
        cairo_version: int = 0,
        nonce: Optional[int] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> "DeployResult":
        """
        Deploys a contract through Universal Deployer Contract

        :param account: BaseAccount used to sign and send deploy transaction.
        :param class_hash: The class_hash of the contract to be deployed.
        :param abi: An abi of the contract to be deployed.
        :param constructor_args: a ``list`` or ``dict`` of arguments for the constructor.
        :param deployer_address: Address of the UDC. Is set to the address of
            the default UDC (same address on mainnet/testnet/devnet) by default.
            Must be set when using custom network other than ones listed above.
        :param cairo_version: Version of the Cairo in which contract is written.
        :param nonce: Nonce of the transaction.
        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation (not recommended, as it may lead to high costs).
        :return: DeployResult instance.
        """
        # pylint: disable=too-many-arguments
        deployer = Deployer(
            deployer_address=deployer_address, account_address=account.address
        )
        deploy_call, address = deployer.create_contract_deployment(
            class_hash=class_hash,
            abi=abi,
            calldata=constructor_args,
            cairo_version=cairo_version,
        )
        res = await account.execute(
            calls=deploy_call, nonce=nonce, max_fee=max_fee, auto_estimate=auto_estimate
        )

        deployed_contract = Contract(
            provider=account, address=address, abi=abi, cairo_version=cairo_version
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
        compiled_contract: str,
        constructor_args: Optional[Union[List, Dict]] = None,
        deployer_address: int = 0,
    ) -> int:
        """
        Computes address for given contract.

        :param salt: int
        :param compiled_contract: String containing compiled contract.
        :param constructor_args: A ``list`` or ``dict`` of arguments for the constructor.
        :param deployer_address: Address of the deployer (if not provided default 0 is used).

        :return: Contract's address.
        """

        compiled = create_compiled_contract(compiled_contract)
        assert compiled.abi is not None
        translated_args = translate_constructor_args(compiled.abi, constructor_args)
        return compute_address(
            salt=salt,
            class_hash=compute_class_hash(compiled),
            constructor_calldata=translated_args,
            deployer_address=deployer_address,
        )

    @staticmethod
    def compute_contract_hash(compiled_contract: str) -> int:
        """
        Computes hash for given contract.

        :param compiled_contract: String containing compiled contract.
        :return: Class_hash of the contract.
        """

        contract_class = create_compiled_contract(compiled_contract)
        return compute_class_hash(contract_class)

    @classmethod
    def _make_functions(
        cls,
        contract_data: ContractData,
        client: Client,
        account: Optional[BaseAccount],
        cairo_version: int = 0,
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


def _unpack_provider(
    provider: Union[BaseAccount, Client]
) -> Tuple[Client, Optional[BaseAccount]]:
    """
    Get the client and optional account to be used by Contract.

    If provided with Client, returns this Client and None.
    If provided with BaseAccount, returns underlying Client and the account.
    """
    if isinstance(provider, Client):
        return provider, None

    if isinstance(provider, BaseAccount):
        return provider.client, provider

    raise ValueError("Argument provider is not of accepted type.")
