import dataclasses
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional, TypeVar, Union, Dict, Collection, NamedTuple

from starkware.cairo.lang.compiler.identifier_manager import IdentifierManager
from starkware.starknet.core.os.contract_hash import compute_contract_hash
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    CastableToHash,
)
from starkware.starkware_utils.error_handling import StarkErrorCode

from starknet_py.net import Client
from starknet_py.net.models import (
    InvokeFunction,
    AddressRepresentation,
    parse_address,
    compute_address,
    compute_invoke_hash,
)
from starknet_py.net.models.address import BlockIdentifier
from starknet_py.utils.compiler.starknet_compile import (
    StarknetCompilationSource,
    starknet_compile,
)
from starknet_py.utils.crypto.facade import pedersen_hash
from starknet_py.utils.data_transformer import DataTransformer
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
    _client: "Client"
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
            int(self.hash, 16),
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
    contract: ContractData = None
    invoke_transaction: InvokeFunction = None

    def __post_init__(self):
        assert self.contract is not None
        assert self.invoke_transaction is not None


InvocationResult = InvokeResult


@add_sync_methods
@dataclass(frozen=True)
class DeployResult(SentTransaction):
    deployed_contract: "Contract" = None

    def __post_init__(self):
        assert self.deployed_contract is not None


# pylint: disable=too-many-instance-attributes
@add_sync_methods
class PreparedFunctionCall:
    def __init__(
        self,
        calldata: List[int],
        arguments: Dict[str, List[int]],
        selector: int,
        client: Client,
        payload_transformer: DataTransformer,
        contract_data: ContractData,
        max_fee: int,
        version: int,
    ):
        # pylint: disable=too-many-arguments
        self.calldata = calldata
        self.arguments = arguments
        self.selector = selector
        self._client = client
        self._payload_transformer = payload_transformer
        self._contract_data = contract_data
        self.max_fee = max_fee
        self.version = version

    @property
    @lru_cache()
    def hash(self) -> int:
        return compute_invoke_hash(
            contract_address=self._contract_data.address,
            entry_point_selector=self.selector,
            calldata=self.calldata,
            chain_id=self._client.chain,
            max_fee=self.max_fee if self.max_fee is not None else 0,
            version=self.version,
        )

    async def call_raw(
        self,
        signature: Optional[Collection[int]] = None,
        block_hash: Optional[str] = None,
        block_number: Optional[int] = None,
    ) -> List[int]:
        """
        Calls a method without translating the result into python values.

        :param signature: Signature to send
        :param block_hash: Optional block hash
        :param block_number: Optional block number
        :return: list of ints
        """
        tx = self._make_invoke_function(signature)
        return await self._client.call_contract(
            invoke_tx=tx, block_hash=block_hash, block_number=block_number
        )

    async def call(
        self,
        signature: Optional[Collection[int]] = None,
        block_hash: Optional[str] = None,
        block_number: Optional[BlockIdentifier] = None,
    ) -> NamedTuple:
        """
        Calls a method.

        :param signature: Signature to send
        :param block_hash: Optional block hash
        :param block_number: Optional block number or "pending" for pending block
        :return: CallResult or List[int] if return_raw is used
        """
        result = await self.call_raw(
            signature=signature, block_hash=block_hash, block_number=block_number
        )
        return self._payload_transformer.to_python(result)

    async def invoke(
        self,
        signature: Optional[Collection[int]] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> InvokeResult:
        """
        Invokes a method.

        :param signature: Signature to send
        :param max_fee: Max amount of Wei to be paid when executing transaction
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs
        :return: InvokeResult
        """
        if auto_estimate and max_fee is not None:
            raise ValueError(
                "Max_fee and auto_estimate are exclusive and cannot be provided at the same time."
            )
        if auto_estimate and self.max_fee is not None:
            raise ValueError(
                "Auto_estimate cannot be used if max_fee was provided when preparing a function call."
            )

        if auto_estimate:
            estimate_fee = await self.estimate_fee()
            max_fee = int(estimate_fee * 1.1)

        if max_fee is not None:
            self.max_fee = max_fee

        if self.max_fee is None:
            raise ValueError("Max_fee must be specified when invoking a transaction")

        tx = self._make_invoke_function(signature=signature)
        response = await self._client.add_transaction(tx=tx)

        if response["code"] != StarkErrorCode.TRANSACTION_RECEIVED.name:
            raise Exception("Failed to send transaction. Response: {response}.")

        invoke_result = InvokeResult(
            hash=response["transaction_hash"],  # noinspection PyTypeChecker
            _client=self._client,
            contract=self._contract_data,
            invoke_transaction=tx,
        )

        return invoke_result

    async def estimate_fee(self):
        """
        Estimate fee for prepared function call

        :return: Estimated amount of Wei executing specified transaction will cost
        :raises ValueError: when max_fee of PreparedFunctionCall is not None or 0.
        """
        if self.max_fee is not None and self.max_fee != 0:
            raise ValueError(
                "Cannot estimate fee of PreparedFunctionCall with max_fee not None or 0."
            )

        tx = self._make_invoke_function(signature=None)
        return await self._client.estimate_fee(tx=tx)

    def _make_invoke_function(self, signature) -> InvokeFunction:
        return InvokeFunction(
            contract_address=self._contract_data.address,
            entry_point_selector=self.selector,
            calldata=self.calldata,
            # List is required here
            signature=[*signature] if signature else [],
            max_fee=self.max_fee if self.max_fee is not None else 0,
            version=self.version,
        )


@add_sync_methods
class ContractFunction:
    def __init__(
        self, name: str, abi: ABIEntry, contract_data: ContractData, client: "Client"
    ):
        self.name = name
        self.abi = abi
        self.inputs = abi["inputs"]
        self.contract_data = contract_data
        self._client = client
        self._payload_transformer = DataTransformer(
            abi=self.abi, identifier_manager=self.contract_data.identifier_manager
        )

    def prepare(
        self,
        *args,
        version: int = 0,
        max_fee: int = None,
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
        block_number: Optional[BlockIdentifier] = None,
        **kwargs,
    ) -> NamedTuple:
        """
        :param block_hash: Block hash to execute the contract at specific point of time
        :param block_number: Block number (or "pending" for pending block) to execute the contract function at

        Call contract's function. ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        The result is translated from Cairo data to python values.
        Equivalent of ``.prepare(*args, **kwargs).call()``.
        """
        return await self.prepare(max_fee=0, version=0, *args, **kwargs).call(
            block_hash=block_hash, block_number=block_number
        )

    async def invoke(
        self, *args, max_fee: int = None, auto_estimate: bool = False, **kwargs
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

    def __init__(self, address: AddressRepresentation, abi: list, client: "Client"):
        """
        Should be used instead of ``from_address`` when ABI is known statically.

        :param address: contract's address
        :param abi: contract's abi
        :param client: client used for API calls
        """
        self._data = ContractData.from_abi(parse_address(address), abi)
        self._functions = self._make_functions(self._data, client)

    @property
    def functions(self) -> FunctionsRepository:
        """
        :return: All functions exposed from a contract.
        """
        return self._functions

    @property
    def address(self) -> int:
        return self._data.address

    @staticmethod
    async def from_address(
        address: AddressRepresentation, client: Client
    ) -> "Contract":
        """
        Fetches ABI for given contract and creates a new Contract instance with it. If you know ABI statically you
        should create Contract's instances directly instead of using this function to avoid unnecessary API calls.

        :raises BadRequest: when contract is not found
        :param address: Contract's address
        :param client: Client used
        :return: an initialized Contract instance
        """
        code = await client.get_code(contract_address=parse_address(address))
        return Contract(address=parse_address(address), abi=code["abi"], client=client)

    @staticmethod
    async def deploy(
        client: Client,
        compilation_source: Optional[StarknetCompilationSource] = None,
        compiled_contract: Optional[str] = None,
        constructor_args: Optional[Union[List[any], dict]] = None,
        salt: Optional[int] = None,
        search_paths: Optional[List[str]] = None,
    ) -> "Contract":
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
        :return: an initialized Contract instance
        """
        definition = Contract._make_definition(
            compilation_source=compilation_source,
            compiled_contract=compiled_contract,
            search_paths=search_paths,
        )
        translated_args = Contract._translate_constructor_args(
            definition, constructor_args
        )
        res = await client.deploy(
            compiled_contract=definition,
            constructor_calldata=translated_args,
            salt=salt,
        )
        contract_address = res["address"]

        deployed_contract = Contract(
            client=client,
            address=contract_address,
            abi=definition.abi,
        )
        deploy_result = DeployResult(
            hash=res["transaction_hash"],
            _client=client,
            deployed_contract=deployed_contract,
        )

        return deploy_result

    @staticmethod
    def compute_address(
        salt: int,
        compilation_source: Optional[StarknetCompilationSource] = None,
        compiled_contract: Optional[str] = None,
        constructor_args: Optional[Union[List[any], dict]] = None,
        search_paths: Optional[List[str]] = None,
    ) -> int:
        """
        Computes address for given contract.
        Either `compilation_source` or `compiled_contract` is required.

        :param salt: int
        :param compilation_source: string containing source code or a list of source files paths
        :param compiled_contract: string containing compiled contract. Useful for reading compiled contract from a file.
        :param constructor_args: a ``list`` or ``dict`` of arguments for the constructor.
        :param search_paths: a ``list`` of paths used by starknet_compile to resolve dependencies within contracts.
        :return: contract's address
        """
        definition = Contract._make_definition(
            compilation_source=compilation_source,
            compiled_contract=compiled_contract,
            search_paths=search_paths,
        )
        translated_args = Contract._translate_constructor_args(
            definition, constructor_args
        )
        return compute_address(
            salt=salt,
            contract_hash=compute_contract_hash(definition, hash_func=pedersen_hash),
            constructor_calldata=translated_args,
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
        :return:
        """
        definition = Contract._make_definition(
            compilation_source=compilation_source,
            compiled_contract=compiled_contract,
            search_paths=search_paths,
        )
        return compute_contract_hash(definition, hash_func=pedersen_hash)

    @staticmethod
    def _make_definition(
        compilation_source: Optional[StarknetCompilationSource] = None,
        compiled_contract: Optional[str] = None,
        search_paths: Optional[List[str]] = None,
    ) -> ContractDefinition:
        if not compiled_contract and not compilation_source:
            raise ValueError(
                "One of compiled_contract or compilation_source is required."
            )

        if not compiled_contract:
            compiled_contract = starknet_compile(
                compilation_source, search_paths=search_paths
            )

        return ContractDefinition.loads(compiled_contract)

    @staticmethod
    def _translate_constructor_args(
        contract: ContractDefinition, constructor_args: any
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
        calldata, _args = DataTransformer(
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
