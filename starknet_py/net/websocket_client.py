import asyncio
import json
from typing import Any, Callable, Dict, List, Optional, Union, cast

from websockets.asyncio.client import ClientConnection, connect

from starknet_py.net.client_models import Hash, LatestTag
from starknet_py.net.client_utils import _to_rpc_felt, get_block_identifier
from starknet_py.net.schemas.rpc.ws import (
    NewEventsNotificationSchema,
    NewHeadsNotificationSchema,
    PendingTransactionsNotificationSchema,
    ReorgNotificationSchema,
    TransactionStatusNotificationSchema,
)
from starknet_py.net.websocket_client_errors import WebsocketClientError
from starknet_py.net.websocket_client_models import (
    NewEventsNotification,
    NewHeadsNotification,
    PendingTransactionsNotification,
    ReorgNotification,
    TransactionStatusNotification,
)

HandlerNotification = Union[
    NewHeadsNotification,
    NewEventsNotification,
    TransactionStatusNotification,
    PendingTransactionsNotification,
    ReorgNotification,
]
Handler = Callable[[HandlerNotification], Any]

_SCHEMA_MAPPING = {
    "starknet_subscriptionNewHeads": NewHeadsNotificationSchema,
    "starknet_subscriptionEvents": NewEventsNotificationSchema,
    "starknet_subscriptionTransactionStatus": TransactionStatusNotificationSchema,
    "starknet_subscriptionPendingTransactions": PendingTransactionsNotificationSchema,
    "starknet_subscriptionReorg": ReorgNotificationSchema,
}


class WebsocketClient:
    """
    Starknet client for WebSocket API.
    """

    connection: ClientConnection

    def __init__(self, node_url: str):
        """
        :param node_url: URL of the node providing the WebSocket API.
        """
        self.node_url: str = node_url
        self._listen_task: Optional[asyncio.Task] = None
        self._subscriptions: Dict[int, Handler] = {}
        self._message_id = 0
        self._pending_responses: Dict[int, asyncio.Future] = {}
        self._reorg_notification_handler: Optional[
            Callable[[ReorgNotification], Any]
        ] = None

    async def connect(self):
        """
        Establishes the WebSocket connection.
        """
        self.connection = await connect(self.node_url)
        self._listen_task = asyncio.create_task(self._listen())

    async def disconnect(self):
        """
        Closes the WebSocket connection.
        """
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        await self.connection.close()

    async def subscribe_new_heads(
        self,
        handler: Callable[[NewHeadsNotification], Any],
        block_hash: Optional[Union[Hash, LatestTag]] = None,
        block_number: Optional[Union[int, LatestTag]] = None,
    ) -> int:
        """
        Creates a WebSocket stream which will fire events for new block headers.

        :param handler: The function to call when a new block header is received.
        :param block_hash: Hash of the block to get notifications from or literal `"latest"`.
            Mutually exclusive with ``block_number`` parameter. If not provided, queries block `"latest"`.
        :param block_number: Number (height) of the block to get notifications from or literal `"latest"`.
        :return: The subscription ID.
        """
        block_id = get_block_identifier(block_hash, block_number, "latest")
        subscription_id = await self._subscribe(
            handler, "starknet_subscribeNewHeads", block_id
        )

        return subscription_id

    @property
    def reorg_notification_handler(
        self,
    ) -> Optional[Callable[[ReorgNotification], Any]]:
        """
        The notifications handler for reorganization of the chain.
        Will be called when subscribing to new heads, events or transaction status.

        :return: The handler for reorg notifications.
        """
        return self._reorg_notification_handler

    @reorg_notification_handler.setter
    def reorg_notification_handler(self, handler: Callable[[ReorgNotification], Any]):
        """
        Sets the handler for reorg notifications.

        :param handler: The handler for reorg notifications.
        """
        self._reorg_notification_handler = handler

    async def subscribe_events(
        self,
        handler: Callable[[NewEventsNotification], Any],
        from_address: Optional[int] = None,
        keys: Optional[List[List[int]]] = None,
        block_hash: Optional[Union[Hash, LatestTag]] = None,
        block_number: Optional[Union[int, LatestTag]] = None,
    ) -> int:
        """
        Creates a WebSocket stream which will fire events for new Starknet events with applied filters.

        :param handler: The function to call when a new event is received.
        :param from_address: Address which emitted the event.
        :param keys: The keys to filter events by.
        :param block_hash: Hash of the block to get notifications from or literal `"latest"`.
            Mutually exclusive with ``block_number`` parameter. If not provided, queries block `"latest"`.
        :param block_number: Number (height) of the block to get notifications from or literal `"latest"`.
        :return: The subscription ID.
        """
        from_address_serialized = _to_rpc_felt(from_address) if from_address else None
        keys_serialized = (
            [[_to_rpc_felt(key) for key in keys] for keys in keys] if keys else None
        )
        block_id = get_block_identifier(block_hash, block_number, "latest")
        params = {
            "from_address": from_address_serialized,
            "keys": keys_serialized,
            "block_id": block_id,
        }
        params = _clear_none_values(params)
        subscription_id = await self._subscribe(
            handler, "starknet_subscribeEvents", params
        )

        return subscription_id

    async def subscribe_transaction_status(
        self,
        handler: Callable[[TransactionStatusNotification], Any],
        transaction_hash: int,
    ) -> int:
        """
        Creates a WebSocket stream which at first fires an event with the current known transaction status, followed
        by events for every transaction status update.

        :param handler: The function to call when a new transaction status is received.
        :param transaction_hash: The transaction hash to fetch status updates for.
        :return: The subscription ID.
        """
        params = {"transaction_hash": _to_rpc_felt(transaction_hash)}
        subscription_id = await self._subscribe(
            handler, "starknet_subscribeTransactionStatus", params
        )

        return subscription_id

    async def subscribe_pending_transactions(
        self,
        handler: Callable[[PendingTransactionsNotification], Any],
        transaction_details: Optional[bool] = None,
        sender_address: Optional[List[int]] = None,
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
            "transaction_details": (
                transaction_details if transaction_details is not None else None
            ),
            "sender_address": (
                [_to_rpc_felt(address) for address in sender_address]
                if sender_address
                else None
            ),
        }
        params = _clear_none_values(params)

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
        res = await self._send_message("starknet_unsubscribe", params)
        unsubscription_result = res["result"]

        if unsubscription_result:
            del self._subscriptions[subscription_id]

        return unsubscription_result

    async def _subscribe(
        self,
        handler: Callable[[Any], Any],
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> int:
        """ "
        Creates a WebSocket stream which will fire events on a specific action.

        :param handler: The function to call when a new notification is received.
        :param method: The method to call to subscribe.
        :param params: The parameters to pass to the method.

        :return: The subscription ID.
        """
        rpc_response = await self._send_message(method, params)
        subscription_id = int(rpc_response["result"])
        self._subscriptions[subscription_id] = handler

        return subscription_id

    async def _listen(self):
        """
        Listens for incoming WebSocket messages.
        """
        async for message in self.connection:
            self._handle_received_message(message)

    async def _send_message(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ):
        """
        Sends a message to the WebSocket server.

        :param method: The method to call.
        :param params: The parameters to pass to the method.
        """
        message_id = self._message_id
        self._message_id += 1

        payload = {
            "id": message_id,
            "jsonrpc": "2.0",
            "method": method,
            "params": params if params else [],
        }

        future = asyncio.get_event_loop().create_future()
        self._pending_responses[message_id] = future

        await self.connection.send(json.dumps(payload))
        response = await future

        if "error" in response:
            self._handle_error(response)

        return response

    def _handle_received_message(self, message: Union[str, bytes]):
        """
        Handles the received message.

        :param message: The message received from the WebSocket server.
        """
        data = cast(Dict, json.loads(message))

        # case when the message is a response to a request
        if "id" in data and data["id"] in self._pending_responses:
            future = self._pending_responses.pop(data["id"])
            future.set_result(data)

        # notification case
        elif "method" in data:
            self._handle_notification(data)

    def _handle_notification(self, data: Dict):
        """
        Handles the received notification.

        :param data: The notification data.
        """
        method = data["method"]
        schema = _SCHEMA_MAPPING[method]
        notification: HandlerNotification = schema().load(data["params"])

        if notification.subscription_id not in self._subscriptions:
            return

        if isinstance(notification, ReorgNotification):
            if self._reorg_notification_handler:
                self._reorg_notification_handler(notification)
        else:
            handler = self._subscriptions[notification.subscription_id]
            handler(notification)

    def _handle_error(self, result: dict):
        # pylint: disable=no-self-use
        raise WebsocketClientError(
            code=result["error"]["code"],
            message=result["error"]["message"],
            data=result["error"].get("data"),
        )


def _clear_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}
