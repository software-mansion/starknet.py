from typing import Any, Callable, Dict, List, Optional, Union, cast

from starknet_py.net.client_models import BlockHeader, EmittedEvent, Hash, Tag
from starknet_py.net.client_utils import _clear_none_values
from starknet_py.net.http_client import RpcHttpClient
from starknet_py.net.schemas.rpc.ws import (
    EventsNotificationSchema,
    NewHeadsNotificationSchema,
    PendingTransactionsNotificationSchema,
    ReorgNotificationSchema,
    SubscribeResponseSchema,
    TransactionStatusNotificationSchema,
    UnsubscribeResponseSchema,
)
from starknet_py.net.ws_client import RpcWSClient
from starknet_py.net.ws_full_node_client_models import (
    EventsNotification,
    NewHeadsNotification,
    NewTransactionStatus,
    PendingTransactionsNotification,
    ReorgNotification,
    SubscribeResponse,
    Transaction,
    TransactionStatusNotification,
    UnsubscribeResponse,
)

BlockId = Union[int, Hash, Tag]
HandlerNotification = Union[
    NewHeadsNotification,
    EventsNotification,
    TransactionStatusNotification,
    PendingTransactionsNotification,
    ReorgNotification,
]
Handler = Callable[[HandlerNotification], Any]


class FullNodeWSClient:
    """
    Starknet WebSocket client for RPC API.
    """

    def __init__(self, node_url: str):
        """
        :param node_url: URL of the node providing the WebSocket API.
        """
        self.node_url: str = node_url
        self._rpc_ws_client: RpcWSClient = RpcWSClient(node_url)
        self._subscriptions: Dict[int, Handler] = {}

    async def connect(self):
        """
        Establishes the WebSocket connection.
        """
        await self._rpc_ws_client.connect()

    async def disconnect(self):
        """
        Closes the WebSocket connection.
        """
        await self._rpc_ws_client.disconnect()

    async def _subscribe(
        self,
        handler: Callable[[Any], Any],
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> int:
        data = await self._rpc_ws_client.send(method, params)
        response = cast(
            SubscribeResponse,
            SubscribeResponseSchema().load(data),
        )

        self._subscriptions[response.subscription_id] = handler

        return response.subscription_id

    async def listen(self):
        """
        Listens for incoming WebSocket messages.
        """
        await self._rpc_ws_client.listen(self._handle_received_message)

    def _handle_received_message(self, message: Dict):
        if "params" not in message:
            # TODO(#1498): Possibly move `handle_rpc_error` from `RpcHttpClient` to separate function
            RpcHttpClient.handle_rpc_error(message)

        subscription_id = message["params"]["subscription_id"]

        if subscription_id not in self._subscriptions:
            return

        handler = self._subscriptions[subscription_id]
        method = message["method"]

        if method == "starknet_subscriptionNewHeads":
            notification = cast(
                NewHeadsNotification,
                NewHeadsNotificationSchema().load(message["params"]),
            )
            handler(notification)

        elif method == "starknet_subscriptionEvents":
            notification = cast(
                EventsNotification,
                EventsNotificationSchema().load(message["params"]),
            )
            handler(notification)

        elif method == "starknet_subscriptionTransactionStatus":
            notification = cast(
                TransactionStatusNotification,
                TransactionStatusNotificationSchema().load(message["params"]),
            )
            handler(notification)

        elif method == "starknet_subscriptionPendingTransactions":
            notification = cast(
                PendingTransactionsNotification,
                PendingTransactionsNotificationSchema().load(message["params"]),
            )
            handler(notification)

        elif method == "starknet_subscriptionReorg":
            notification = cast(
                ReorgNotification,
                ReorgNotificationSchema().load(message["params"]),
            )
            handler(notification)

    async def subscribe_new_heads(
        self,
        handler: Callable[[BlockHeader], Any],
        block: Optional[BlockId],
    ) -> int:
        """
        Creates a WebSocket stream which will fire events for new block headers.

        :param handler: The function to call when a new block header is received.
        :param block: The block to get notifications from, default is latest, limited to 1024 blocks back.
        :return: The subscription ID.
        """
        params = {"block": block} if block else {}
        subscription_id = await self._subscribe(
            handler, "starknet_subscribeNewHeads", params
        )

        return subscription_id

    async def subscribe_events(
        self,
        handler: Callable[[EmittedEvent], Any],
        from_address: Optional[int] = None,
        keys: Optional[List[List[int]]] = None,
        block: Optional[BlockId] = None,
    ) -> int:
        """
        Creates a WebSocket stream which will fire events for new Starknet events with applied filters.

        :param handler: The function to call when a new event is received.
        :param from_address: Address which emitted the event.
        :param keys: The keys to filter events by.
        :param block: The block to get notifications from, default is latest, limited to 1024 blocks back.
        :return: The subscription ID.
        """
        params = {"from_address": from_address, "keys": keys, "block": block}
        subscription_id = await self._subscribe(
            handler, "starknet_subscribeEvents", params
        )

        return subscription_id

    async def subscribe_transaction_status(
        self,
        handler: Callable[[NewTransactionStatus], Any],
        transaction_hash: int,
        block: Optional[BlockId] = None,
    ) -> int:
        """
        Creates a WebSocket stream which will fire events when a transaction status is updated.

        :param handler: The function to call when a new transaction status is received.
        :param transaction_hash: The transaction hash to fetch status updates for.
        :param block: The block to get notifications from, default is latest, limited to 1024 blocks back.
        :return: The subscription ID.
        """
        params = {"transaction_hash": transaction_hash, "block": block}
        params = _clear_none_values(params)
        subscription_id = await self._subscribe(
            handler, "starknet_subscribeTransactionStatus", params
        )

        return subscription_id

    async def subscribe_pending_transactions(
        self,
        handler: Callable[[Union[int, Transaction]], Any],
        transaction_details: Optional[bool],
        sender_address: Optional[List[int]],
    ) -> int:
        """
        Creates a WebSocket stream which will fire events when a new pending transaction is added.
        While there is no mempool, this notifies of transactions in the pending block.

        :param handler: The function to call when a new pending transaction is received.
        :param transaction_details: Whether to include transaction details in the notification.
        If false, only hash is returned.
        :param sender_address: The sender address to filter transactions by.
        :return: The subscription ID.
        """
        params = {
            "transaction_details": transaction_details,
            "sender_address": sender_address,
        }
        subscription_id = await self._subscribe(
            handler, "starknet_subscribePendingTransactions", params
        )

        return subscription_id

    async def unsubscribe(self, subscription_id: int) -> bool:
        """
        Close a previously opened WebSocket stream, with the corresponding subscription id.

        :param subscription_id: ID of the subscription to close.
        :return: True if the unsubscription was successful, False otherwise.
        """
        if subscription_id not in self._subscriptions:
            return False

        params = {"subscription_id": subscription_id}
        res = await self._rpc_ws_client.send("starknet_unsubscribe", params)

        unsubscribe_response = cast(
            UnsubscribeResponse, UnsubscribeResponseSchema().load(res)
        )

        if unsubscribe_response:
            del self._subscriptions[subscription_id]

        return unsubscribe_response.result
