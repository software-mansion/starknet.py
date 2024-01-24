from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import List, Optional, Union

from starknet_py.abi import Abi, AbiParser
from starknet_py.abi.v1.model import Abi as AbiV1
from starknet_py.abi.v1.parser import AbiParser as AbiV1Parser
from starknet_py.abi.v2.model import Abi as AbiV2
from starknet_py.abi.v2.parser import AbiParser as AbiV2Parser
from starknet_py.abi.v2.shape import L1_HANDLER_ENTRY
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client import Client
from starknet_py.net.client_models import Call, EstimatedFee, Hash, ResourceBounds, Tag
from starknet_py.net.models.transaction import Invoke
from starknet_py.sent_transaction import SentTransaction
from starknet_py.serialization import (
    FunctionSerializationAdapter,
    TupleDataclass,
    serializer_for_function,
)
from starknet_py.serialization.factory import serializer_for_function_v1
from starknet_py.utils.constructor_args_translator import _is_abi_v2
from starknet_py.utils.sync import add_sync_methods

ABI = list
ABIEntry = dict


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


@dataclass
class CallToSend(Call):
    _client: Client
    _payload_transformer: FunctionSerializationAdapter


@add_sync_methods
@dataclass
class PreparedFunctionCall(CallToSend):
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


@add_sync_methods
@dataclass
class PreparedFunctionInvoke(ABC, CallToSend):
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
            (or "latest" / "pending" for the latest / pending block), default is "pending".
        :param nonce: Nonce of the transaction.
        :return: Estimated amount of the transaction cost, either in Wei or Fri associated with executing the
            specified transaction.
        """

    async def _invoke(self, transaction: Invoke) -> InvokeResult:
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
class PreparedFunctionInvokeV1(PreparedFunctionInvoke):
    max_fee: Optional[int]

    async def invoke(
        self,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        *,
        nonce: Optional[int] = None,
    ) -> InvokeResult:
        """
        Send an Invoke transaction version 1 for a prepared data.

        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :param nonce: Nonce of the transaction.
        :return: InvokeResult.
        """

        transaction = await self.get_account.sign_invoke_v1_transaction(
            calls=self,
            nonce=nonce,
            max_fee=max_fee or self.max_fee,
            auto_estimate=auto_estimate,
        )

        return await self._invoke(transaction)

    async def estimate_fee(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
        *,
        nonce: Optional[int] = None,
    ) -> EstimatedFee:
        tx = await self.get_account.sign_invoke_v1_transaction(
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
@dataclass
class PreparedFunctionInvokeV3(PreparedFunctionInvoke):
    l1_resource_bounds: Optional[ResourceBounds]

    async def invoke(
        self,
        l1_resource_bounds: Optional[ResourceBounds] = None,
        auto_estimate: bool = False,
        *,
        nonce: Optional[int] = None,
    ) -> InvokeResult:
        """
        Send an Invoke transaction version 3 for a prepared data.

        :param l1_resource_bounds: Max amount and max price per unit of L1 gas (in Wei) used when executing
            this transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :param nonce: Nonce of the transaction.
        :return: InvokeResult.
        """

        transaction = await self.get_account.sign_invoke_v3_transaction(
            calls=self,
            nonce=nonce,
            l1_resource_bounds=l1_resource_bounds or self.l1_resource_bounds,
            auto_estimate=auto_estimate,
        )

        return await self._invoke(transaction)

    async def estimate_fee(
        self,
        block_hash: Optional[Union[Hash, Tag]] = None,
        block_number: Optional[Union[int, Tag]] = None,
        *,
        nonce: Optional[int] = None,
    ) -> EstimatedFee:
        tx = await self.get_account.sign_invoke_v3_transaction(
            calls=self, nonce=nonce, l1_resource_bounds=ResourceBounds.init_with_zeros()
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
    ) -> TupleDataclass:
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

    def prepare_invoke_v1(
        self,
        *args,
        max_fee: Optional[int] = None,
        **kwargs,
    ) -> PreparedFunctionInvokeV1:
        """
        ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        Creates a ``PreparedFunctionInvokeV1`` instance which exposes calldata for every argument
        and adds more arguments when calling methods.

        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :return: PreparedFunctionCall.
        """

        calldata = self._payload_transformer.serialize(*args, **kwargs)
        return PreparedFunctionInvokeV1(
            to_addr=self.contract_data.address,
            calldata=calldata,
            selector=self.get_selector(self.name),
            max_fee=max_fee,
            _contract_data=self.contract_data,
            _client=self.client,
            _account=self.account,
            _payload_transformer=self._payload_transformer,
        )

    async def invoke_v1(
        self,
        *args,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        nonce: Optional[int] = None,
        **kwargs,
    ) -> InvokeResult:
        """
        Invoke contract's function. ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        Equivalent of ``.prepare_invoke_v1(*args, **kwargs).invoke()``.

        :param max_fee: Max amount of Wei to be paid when executing transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :param nonce: Nonce of the transaction.
        :return: InvokeResult.
        """
        prepared_invoke = self.prepare_invoke_v1(*args, **kwargs)
        return await prepared_invoke.invoke(
            max_fee=max_fee, nonce=nonce, auto_estimate=auto_estimate
        )

    def prepare_invoke_v3(
        self,
        *args,
        l1_resource_bounds: Optional[ResourceBounds] = None,
        **kwargs,
    ) -> PreparedFunctionInvokeV3:
        """
        ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        Creates a ``PreparedFunctionInvokeV3`` instance which exposes calldata for every argument
        and adds more arguments when calling methods.

        :param l1_resource_bounds: Max amount and max price per unit of L1 gas (in Wei) used when executing
            this transaction.
        :return: PreparedFunctionInvokeV3.
        """

        calldata = self._payload_transformer.serialize(*args, **kwargs)
        return PreparedFunctionInvokeV3(
            to_addr=self.contract_data.address,
            calldata=calldata,
            selector=self.get_selector(self.name),
            l1_resource_bounds=l1_resource_bounds,
            _contract_data=self.contract_data,
            _client=self.client,
            _account=self.account,
            _payload_transformer=self._payload_transformer,
        )

    async def invoke_v3(
        self,
        *args,
        l1_resource_bounds: Optional[ResourceBounds] = None,
        auto_estimate: bool = False,
        nonce: Optional[int] = None,
        **kwargs,
    ) -> InvokeResult:
        """
        Invoke contract's function. ``*args`` and ``**kwargs`` are translated into Cairo calldata.
        Equivalent of ``.prepare_invoke_v3(*args, **kwargs).invoke()``.

        :param l1_resource_bounds: Max amount and max price per unit of L1 gas (in Wei) used when executing
            this transaction.
        :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
        :param nonce: Nonce of the transaction.
        :return: InvokeResult.
        """
        prepared_invoke = self.prepare_invoke_v3(*args, **kwargs)
        return await prepared_invoke.invoke(
            l1_resource_bounds=l1_resource_bounds,
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
