import dataclasses
import json
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING, Union

from starkware.cairo.lang.compiler.identifier_manager import IdentifierManager
from starkware.starknet.definitions.fields import ContractAddressSalt
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    CastableToHash,
)
from starkware.starkware_utils.error_handling import StarkErrorCode

from .utils.compiler.starknet_compile import StarknetCompilationSource, starknet_compile
from .utils.data_transformer import DataTransformer
from .utils.types import AddressRepresentation, parse_address, InvokeFunction, Deploy
from .utils.sync import add_sync_version

ABI = list
ABIEntry = dict

if TYPE_CHECKING:
    from .net import Client


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


@add_sync_version
@dataclass(frozen=True)
class InvocationResult:
    """
    Dataclass returned from invocation. Contains basic details and allows waiting for transaction's acceptance.
    """

    hash: CastableToHash
    contract: ContractData
    _client: "Client"
    status: Optional[str] = None
    block_number: Optional[int] = None

    async def wait_for_acceptance(
        self, wait_for_accept: Optional[bool] = False, check_interval=5
    ) -> "InvocationResult":
        """
        Waits for invoke transaction to be accepted on chain. By default, returns when status is ``PENDING`` -
        use ``wait_for_accept`` to wait till ``ACCEPTED`` status.
        Returns a new InvocationResult instance, **does not mutate original instance**.
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


@add_sync_version
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

    async def call(
        self,
        *args,
        block_hash: Optional[str] = None,
        block_number: Optional[int] = None,
        signature: Optional[List[str]] = None,
        return_raw: bool = False,
        **kwargs,
    ):
        """
        Call contract's function. ``*args`` and ``**kwargs`` are translated into Cairo types.
        """
        tx = self._make_invoke_function(*args, signature=signature, **kwargs)
        result = await self._client.call_contract(
            invoke_tx=tx, block_hash=block_hash, block_number=block_number
        )
        if return_raw:
            return result
        return self._payload_transformer.to_python(result)

    async def invoke(
        self, *args, signature: Optional[List[str]] = None, **kwargs
    ) -> InvocationResult:
        """
        Invoke contract's function. ``*args`` and ``**kwargs`` are translated into Cairo types.
        """
        tx = self._make_invoke_function(*args, signature=signature, **kwargs)
        response = await self._client.add_transaction(tx=tx)

        if response["code"] != StarkErrorCode.TRANSACTION_RECEIVED.name:
            raise Exception("Failed to send transaction. Response: {response}.")

        return InvocationResult(
            hash=response["transaction_hash"],  # noinspection PyTypeChecker
            contract=self.contract_data,
            _client=self._client,
        )

    @property
    def selector(self):
        return get_selector_from_name(self.name)

    def _make_invoke_function(self, *args, signature=None, **kwargs):
        return InvokeFunction(
            contract_address=self.contract_data.address,
            entry_point_selector=self.selector,
            calldata=self._payload_transformer.from_python(*args, **kwargs),
            signature=signature or [],
        )


@add_sync_version
class ContractFunctionsRepository:
    """
    Contains functions exposed from a contract. They are set as properties during initialization.
    """

    def __init__(self, contract_data: ContractData, client: "Client"):
        for abi_entry in contract_data.abi:
            if abi_entry["type"] != "function":
                continue

            name = abi_entry["name"]
            setattr(
                self,
                name,
                ContractFunction(
                    name=name,
                    abi=abi_entry,
                    contract_data=contract_data,
                    client=client,
                ),
            )


@add_sync_version
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
        self._functions = ContractFunctionsRepository(self._data, client)

    @property
    def functions(self) -> ContractFunctionsRepository:
        """
        :return: All functions exposed from a contract.
        """
        return self._functions

    @property
    def address(self) -> int:
        return self._data.address

    @staticmethod
    async def from_address(
        address: AddressRepresentation, client: "Client"
    ) -> "Contract":
        """
        Fetches ABI for given contract and creates a new Contract instance with it. If you know ABI statically you
        should create Contract's instances directly instead of using this function to avoid unnecessary API calls.

        :param address: Contract's address
        :param client: Client used
        :return: contract
        """
        code = await client.get_code(contract_address=parse_address(address))
        return Contract(address=parse_address(address), abi=code["abi"], client=client)

    @staticmethod
    async def deploy(
        client: "Client",
        compilation_source: Optional[StarknetCompilationSource] = None,
        compiled_contract: Optional[str] = None,
        constructor_args: Optional[Union[List[any], dict]] = None,
    ) -> "Contract":
        """
        Deploys a contract and waits until it has PENDING status. Either compilation_source or compiled_contract is required.

        :param client: Client
        :param compilation_source: string of source code or a dict {FILENAME: CONTENT}.
        :param compiled_contract: string containing compiled contract. Useful for reading compiled contract from a file.
        :param constructor_args: a list or dict of arguments for the constructor.
        :return:
        """
        if not compiled_contract and not compilation_source:
            raise ValueError(
                "At least one of compiled_contract, compilation_source is required for contract deployment."
            )

        if not compiled_contract:
            compiled_contract = starknet_compile(compilation_source)

        abi = json.loads(compiled_contract)["abi"]
        translated_args = Contract._translate_constructor_args(abi, constructor_args)

        res = await client.add_transaction(
            tx=Deploy(
                contract_address_salt=ContractAddressSalt.get_random_value(),
                contract_definition=ContractDefinition.loads(compiled_contract),
                constructor_calldata=translated_args,
            )
        )

        assert res["code"] == StarkErrorCode.TRANSACTION_RECEIVED.name
        contract_address = res["address"]

        await client.wait_for_tx(
            tx_hash=res["transaction_hash"],
        )

        return Contract(
            client=client,
            address=contract_address,
            abi=abi,
        )

    @staticmethod
    def _translate_constructor_args(abi: list, constructor_args: any) -> List[int]:
        constructor_abi = next(
            (member for member in abi if member["type"] == "constructor"),
            None,
        )

        if not constructor_abi:
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
        return DataTransformer(
            constructor_abi, identifier_manager_from_abi(abi)
        ).from_python(*args, **kwargs)
