import dataclasses
from dataclasses import dataclass
from typing import List, Optional

from starkware.cairo.lang.compiler.identifier_manager import IdentifierManager
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import (
    CastableToHash,
)
from starkware.starknet.services.api.gateway.transaction import InvokeFunction
from starkware.starkware_utils.error_handling import StarkErrorCode

from .utils.data_transformer import DataTransformer
from .net import Client
from .utils.types import AddressRepresentation, parse_address
from .utils.sync import add_sync_version

ABI = list
ABIEntry = dict


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
    hash: CastableToHash
    contract: ContractData
    _client: Client
    status: Optional[str] = None
    block_number: Optional[int] = None

    async def wait_for_acceptance(
        self, wait_for_accept: Optional[bool] = False, check_interval=5
    ) -> "InvocationResult":
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
        self, name: str, abi: ABIEntry, contract_data: ContractData, client: Client
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
        tx = self._make_invoke_function(*args, signature=signature, **kwargs)
        result = await self._client.call_contract(
            invoke_tx=tx, block_hash=block_hash, block_number=block_number
        )
        if return_raw:
            return result
        return self._payload_transformer.to_python(result)

    async def invoke(self, *args, signature: Optional[List[str]] = None, **kwargs):
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
    def __init__(self, contract_data: ContractData, client: Client):
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
    def __init__(self, address: AddressRepresentation, abi: list, client: Client):
        self.data = ContractData.from_abi(parse_address(address), abi)
        self.functions = ContractFunctionsRepository(self.data, client)

    @staticmethod
    async def from_address(
        address: AddressRepresentation, client: Client
    ) -> "Contract":
        code = await client.get_code(contract_address=parse_address(address))
        return Contract(address=parse_address(address), abi=code["abi"], client=client)
