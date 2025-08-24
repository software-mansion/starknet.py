"""
Client for interacting with the Applicative Paymaster API.

This module provides a client for interacting with the Applicative Paymaster API
as specified in the JSON-RPC specification.
"""

from abc import ABC
from typing import List, Optional, cast

import aiohttp

from starknet_py.net.client_models import Hash
from starknet_py.net.client_utils import _to_rpc_felt
from starknet_py.net.http_client import RpcHttpClient
from starknet_py.net.paymaster.models import (
    BuildTransactionResponse,
    ExecutableUserTransaction,
    ExecuteTransactionResponse,
    TokenData,
    TrackingIdResponse,
    UserParameters,
    UserTransaction,
)
from starknet_py.net.schemas.paymaster import (
    BuildTransactionResponseSchema,
    ExecutableUserTransactionSchema,
    ExecuteTransactionResponseSchema,
    TokenDataSchema,
    TrackingIdResponseSchema,
    UserParametersSchema,
    UserTransactionSchema,
)
from starknet_py.utils.sync import add_sync_methods


@add_sync_methods
class PaymasterClient(ABC):
    """
    Client for interacting with the Applicative Paymaster API.
    """

    def __init__(
        self,
        node_url: str,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Initialize PaymasterClient.

        :param node_url: URL of the paymaster service
        :param session: Aiohttp session to be used for requests. If not provided, a client will create a session for
                        every request. When using a custom session, the user is responsible for closing it manually.
        """
        self.url = node_url
        self._client = RpcHttpClient(
            url=node_url, session=session, method_prefix="paymaster"
        )

    async def is_available(self) -> bool:
        """
        Returns the status of the paymaster service.

        :return: If the paymaster service is correctly functioning, return true. Else, return false.
        """
        return await self._client.call(method_name="isAvailable")

    async def get_supported_tokens(self) -> List[TokenData]:
        """
        Get a list of the tokens that the paymaster supports, together with their prices in STRK.

        :return: An array of token data
        """
        res = await self._client.call(method_name="getSupportedTokens")
        return cast(List[TokenData], TokenDataSchema().load(res, many=True))

    async def tracking_id_to_latest_hash(self, tracking_id: Hash) -> TrackingIdResponse:
        """
        Get the hash of the latest transaction broadcasted by the paymaster corresponding to the requested ID
        and the status of the ID.

        :param tracking_id: A unique identifier used to track an execution request of a user
        :return: The hash of the latest transaction broadcasted by the paymaster corresponding to the requested ID
                and the status of the ID
        """
        res = await self._client.call(
            method_name="trackingIdToLatestHash",
            params={"tracking_id": (_to_rpc_felt(tracking_id))},
        )
        return cast(TrackingIdResponse, TrackingIdResponseSchema().load(res))

    async def build_transaction(
        self, transaction: UserTransaction, parameters: UserParameters
    ) -> BuildTransactionResponse:
        """
        Receives the transaction the user wants to execute. Returns the typed data along with the estimated gas cost
        and the maximum gas cost suggested to ensure execution.

        :param transaction: Transaction to be executed by the paymaster
        :param parameters: Execution parameters to be used when executing the transaction
        :return: The transaction data required for execution along with an estimation of the fee
        """
        # Convert transaction to dict for JSON serialization

        res = await self._client.call(
            method_name="buildTransaction",
            params={
                "transaction": UserTransactionSchema().dump(obj=transaction),
                "parameters": UserParametersSchema().dump(obj=parameters),
            },
        )

        return BuildTransactionResponseSchema().load(res)

    async def execute_transaction(
        self, transaction: ExecutableUserTransaction, parameters: UserParameters
    ) -> ExecuteTransactionResponse:
        """
        Sends the signed typed data to the paymaster service for execution.

        :param transaction: Typed data build by calling paymaster_buildTransaction signed by the user
                           to be executed by the paymaster service
        :param parameters: Execution parameters to be used when executing the transaction
        :return: The hash of the transaction broadcasted by the paymaster and the tracking ID
                corresponding to the user `execute` request
        """
        res = await self._client.call(
            method_name="executeTransaction",
            params={
                "transaction": ExecutableUserTransactionSchema().dump(obj=transaction),
                "parameters": UserParametersSchema().dump(obj=parameters),
            },
        )

        return cast(
            ExecuteTransactionResponse, ExecuteTransactionResponseSchema().load(res)
        )
