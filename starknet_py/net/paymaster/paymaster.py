from abc import ABC, abstractmethod
from typing import Optional

from starknet_py.net.client_models import Calls, OutsideExecutionTimeBounds
from starknet_py.net.paymaster.client import PaymasterClient
from starknet_py.net.paymaster.models import FeeMode, BuildTransactionResponse


class BasePaymaster(ABC):
    @abstractmethod
    async def client(self) -> PaymasterClient:
        """
        Get the PaymasterClient used by the Paymaster.
        """

    @abstractmethod
    async def execute(
        self,
        *,
        calls: Calls,
        fee_mode: FeeMode,
        execution_time_bounds: Optional[OutsideExecutionTimeBounds] = None,
    ):
        """
        Takes calls and token and executes a transaction through the paymaster service.
        """

    @abstractmethod
    async def sign(
        self,
        *,
        calls: Calls,
        fee_mode: FeeMode,
        execution_time_bounds: Optional[OutsideExecutionTimeBounds] = None,
    ) -> BuildTransactionResponse:
        """
        Takes calls and token and crates a transaction through the paymaster service without executing it.
        """
