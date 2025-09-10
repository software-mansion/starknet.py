import asyncio
import json
from typing import Any, Callable, Dict, List, Literal, Optional, Union, cast

from websockets import InvalidState, State
from websockets.asyncio.client import ClientConnection, connect

from starknet_py.net.client_models import (
    Hash,
    LatestTag,
    TransactionFinalityStatusWithoutL1,
    TransactionStatusWithoutL1,
)
from starknet_py.net.client_utils import _to_rpc_felt, get_block_identifier
from starknet_py.net.schemas.rpc.websockets import (
    NewEventsNotificationSchema,
    NewHeadsNotificationSchema,
    NewTransactionNotificationSchema,
    NewTransactionReceiptsNotificationSchema,
    ReorgNotificationSchema,
    TransactionStatusNotificationSchema,
)
from starknet_py.net.websockets.errors import WebsocketClientError
from starknet_py.net.websockets.models import (
    NewEventsNotification,
    NewHeadsNotification,
    NewTransactionNotification,
    NewTransactionReceiptsNotification,
    ReorgNotification,
    TransactionStatusNotification,
)

Notification = Union[
    NewHeadsNotification,
    NewEventsNotification,
    TransactionStatusNotification,
    ReorgNotification,
]
NotificationHandler = Callable[[Notification], Any]

NotificationMethod = Literal[
    "starknet_subscriptionNewHeads",
    "starknet_subscriptionEvents",
    "starknet_subscriptionTransactionStatus",
    "starknet_subscriptionReorg",
    "starknet_subscriptionNewTransactionReceipts",
    "starknet_subscriptionNewTransaction",
]

_NOTIFICATION_SCHEMA_MAPPING = {
    "starknet_subscriptionNewHeads": NewHeadsNotificationSchema,
    "starknet_subscriptionEvents": NewEventsNotificationSchema,
    "starknet_subscriptionTransactionStatus": TransactionStatusNotificationSchema,
    "starknet_subscriptionReorg": ReorgNotificationSchema,
    "starknet_subscriptionNewTransactionReceipts": NewTransactionReceiptsNotificationSchema,
    "starknet_subscriptionNewTransaction": NewTransactionNotificationSchema,
}


# pylint: disable=too-many-instance-attributes
class WebsocketClient:
    """
    Starknet client for WebSocket API.
    """

    def __init__(self, node_url: str):
        """
        :param node_url: URL of the node providing the WebSocket API.
        """
        self.node_url: str = node_url
        self.connection: Optional[ClientConnection] = None
        self._listen_task: Optional[asyncio.Task] = None
        self._subscriptions: Dict[str, NotificationHandler] = {}
        self._message_id = 0
        self._pending_responses: Dict[int, asyncio.Future] = {}
        self._pending_notifications: Dict[str, List[Notification]] = {}
        self._on_chain_reorg: Optional[Callable[[ReorgNotification], Any]] = None

        # Future that completes with an exception if listen loop dies
        self._listen_failed: Optional[asyncio.Future] = None

    async def connect(self):
        """
        Establishes the WebSocket connection.
        """
        self.connection = await connect(
            self.node_url, ping_interval=None, ping_timeout=None
        )

        # Create/reset the failure future for this connection
        loop = asyncio.get_running_loop()
        self._listen_failed = loop.create_future()

        # Start listener and attach a synchronous done-callback
        self._listen_task = asyncio.create_task(self._listen())
        self._listen_task.add_done_callback(self._fail_fast)

    async def disconnect(self):
        """
        Closes the WebSocket connection.
        """
        if self.connection is None:
            raise InvalidState("Connection is not established.")

        if self._listen_task:
            self._listen_task.cancel()
            await asyncio.gather(self._listen_task, return_exceptions=True)
            self._listen_task = None

        # Make sure waiters on _listen_failed don't hang forever
        if self._listen_failed and not self._listen_failed.done():
            self._listen_failed.cancel()

        await self.connection.close()
        self.connection = None

    @property
    async def is_connected(self) -> bool:
        """
        Checks if the WebSocket connection is established.

        :return: True if the connection is established, False otherwise.
        """
        return self.connection is not None and self.connection.state == State.OPEN

    async def subscribe_new_heads(
        self,
        handler: Callable[[NewHeadsNotification], Any],
        block_hash: Optional[Union[Hash, LatestTag]] = None,
        block_number: Optional[Union[int, LatestTag]] = None,
    ) -> str:
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

    # pylint: disable=too-many-arguments
    async def subscribe_events(
        self,
        handler: Callable[[NewEventsNotification], Any],
        from_address: Optional[int] = None,
        keys: Optional[List[List[int]]] = None,
        block_hash: Optional[Union[Hash, LatestTag]] = None,
        block_number: Optional[Union[int, LatestTag]] = None,
        finality_status: Optional[TransactionFinalityStatusWithoutL1] = None,
    ) -> str:
        """
        Creates a WebSocket stream which will fire events for new Starknet events with applied filters.

        :param handler: The function to call when a new event is received.
        :param from_address: Address which emitted the event.
        :param keys: The keys to filter events by.
        :param block_hash: Hash of the block to get notifications from or literal `"latest"`.
            Mutually exclusive with ``block_number`` parameter. If not provided, queries block `"latest"`.
        :param block_number: Number (height) of the block to get notifications from or literal `"latest"`.
        :param finality_status: The finality status of the most recent events to include, default is ACCEPTED_ON_L2.
            If PRE_CONFIRMED finality is selected, events might appear multiple times,
            once for each finality status update.
        :return: The subscription ID.
        """
        params = {}
        if from_address is not None:
            params["from_address"] = _to_rpc_felt(from_address)
        if keys is not None:
            params["keys"] = [
                [_to_rpc_felt(key) for key in key_group] for key_group in keys
            ]
        if finality_status is not None:
            params["finality_status"] = finality_status.value

        block_id = get_block_identifier(block_hash, block_number, "latest")
        params = {
            **params,
            **block_id,
        }

        subscription_id = await self._subscribe(
            handler, "starknet_subscribeEvents", params
        )

        return subscription_id

    async def subscribe_transaction_status(
        self,
        handler: Callable[[TransactionStatusNotification], Any],
        transaction_hash: int,
    ) -> str:
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

    async def subscribe_new_transactions(
        self,
        handler: Callable[[NewTransactionNotification], Any],
        sender_address: Optional[List[int]] = None,
        finality_status: Optional[List[TransactionStatusWithoutL1]] = None,
    ) -> str:
        """
        Creates a WebSocket stream which will fire events when a new pending transaction is added.
        While there is no mempool, this notifies of transactions in the pending block.

        :param handler: The function to call when a new pending transaction is received.
        :param sender_address: List of sender addresses to filter transactions by.
        :param finality_status: The finality statuses to filter transaction receipts by, default is [ACCEPTED_ON_L2].

        :return: The subscription ID.
        """
        params = {}
        if sender_address is not None:
            params["sender_address"] = [
                _to_rpc_felt(address) for address in sender_address
            ]
        if finality_status is not None:
            params["finality_status"] = [status.value for status in finality_status]

        subscription_id = await self._subscribe(
            handler, "starknet_subscribeNewTransactions", params
        )
        return subscription_id

    async def subscribe_new_transaction_receipts(
        self,
        handler: Callable[[NewTransactionReceiptsNotification], Any],
        finality_status: Optional[List[TransactionFinalityStatusWithoutL1]] = None,
        sender_address: Optional[List[int]] = None,
    ) -> str:
        """
        Creates a WebSocket stream which will fire events when new transaction receipts are created.
        An event is fired for each finality status update. It is possible for receipts of pre-confirmed transactions
        to be received multiple times, or not at all.

        :param handler: The function to call when a new pending transaction is received.
        :param finality_status: The finality statuses to filter transaction receipts by, default is [ACCEPTED_ON_L2].
        :param sender_address: List of addresses to filter transactions by.

        :return: The subscription ID.
        """
        params = {}

        if sender_address is not None:
            params["sender_address"] = [
                _to_rpc_felt(address) for address in sender_address
            ]
        if finality_status is not None:
            params["finality_status"] = [status.value for status in finality_status]

        subscription_id = await self._subscribe(
            handler, "starknet_subscribeNewTransactionReceipts", params
        )
        return subscription_id

    @property
    def on_chain_reorg(
        self,
    ) -> Optional[Callable[[ReorgNotification], Any]]:
        """
        The notifications handler for reorganization of the chain.
        Will be called when subscribing to new heads, events or transaction status.

        :return: The handler for reorg notifications.
        """
        return self._on_chain_reorg

    @on_chain_reorg.setter
    def on_chain_reorg(self, handler: Callable[[ReorgNotification], Any]):
        """
        Sets the handler for chain reorg notifications.

        :param handler: The handler for chain reorg notifications.
        """
        self._on_chain_reorg = handler

    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Close a previously opened WebSocket stream, with the corresponding subscription id.

        :param subscription_id: ID of the subscription to close.
        :return: True if the unsubscription was successful, False otherwise.
        """
        if subscription_id not in self._subscriptions:
            return False

        params = {"subscription_id": subscription_id}
        res = await self._send_message("starknet_unsubscribe", params)
        unsubscribe_result: bool = res["result"]

        if unsubscribe_result:
            del self._subscriptions[subscription_id]

        return unsubscribe_result

    async def _subscribe(
        self,
        handler: Callable[[Any], Any],
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """ "
        Creates a WebSocket stream which will fire events on a specific action.

        :param handler: The function to call when a new notification is received.
        :param method: The method to call to subscribe.
        :param params: The parameters to pass to the method.

        :return: The subscription ID.
        """
        response_message = await self._send_message(method, params)
        subscription_id = response_message["result"]
        self._subscriptions[subscription_id] = handler

        pending = self._pending_notifications.pop(subscription_id, [])
        for notification in pending:
            handler(notification)

        return subscription_id

    async def _listen(self):
        """
        Listens for incoming WebSocket messages.
        """
        if self.connection is None:
            raise InvalidState("Connection is not established.")

        while True:
            message = await self.connection.recv()
            self._handle_received_message(message)

    def _fail_fast(self, task: asyncio.Task) -> None:
        if task.cancelled():
            # Propagate cancellation to waiters
            if self._listen_failed and not self._listen_failed.done():
                self._listen_failed.cancel()
            return

        exc = task.exception()
        if exc is not None:
            # Signal failure to all waiters
            if self._listen_failed and not self._listen_failed.done():
                self._listen_failed.set_exception(exc)

            # Also fail any pending RPC futures to unblock callers
            for fut in self._pending_responses.values():
                if not fut.done():
                    fut.set_exception(exc)
            self._pending_responses.clear()

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
        if self.connection is None:
            raise InvalidState("Connection is not established.")

        # If the listener already failed, raise immediately
        if self._listen_failed and self._listen_failed.done():
            await self._listen_failed

        message_id = self._message_id
        self._message_id += 1

        payload = {
            "id": message_id,
            "jsonrpc": "2.0",
            "method": method,
            "params": params if params else [],
        }

        future = asyncio.get_running_loop().create_future()
        self._pending_responses[message_id] = future

        await self.connection.send(json.dumps(payload))

        if self._listen_failed is not None:
            # Get the first future that completes
            done, _ = await asyncio.wait(
                {future, self._listen_failed},
                return_when=asyncio.FIRST_COMPLETED,
            )
            done_future = next(iter(done))
            # If the first completed future was `_listen_failed`, an exception will be raised on awaiting
            response = await done_future
        else:
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

        # case when the message is a response to `subscribe_{method}`
        if "id" in data and data["id"] in self._pending_responses:
            future = self._pending_responses.pop(data["id"])
            future.set_result(data)
        # Case when the message is a notification
        elif "method" in data:
            self._handle_notification(data)
        else:
            raise ValueError(f"Unexpected message: {data}")

    def _handle_notification(self, data: Dict):
        """
        Handles the received notification.

        :param data: The notification data.
        """
        method: NotificationMethod = data["method"]
        schema = _NOTIFICATION_SCHEMA_MAPPING[method]
        notification: Notification = schema().load(data["params"])

        # Notification may arrive before the subscription is registered
        if notification.subscription_id not in self._subscriptions:
            self._pending_notifications.setdefault(
                notification.subscription_id, []
            ).append(notification)
            return

        if isinstance(notification, ReorgNotification):
            if self._on_chain_reorg:
                self._on_chain_reorg(notification)
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

    # Optional: public awaitable for callers that want to detect failure or closure explicitly
    async def wait_closed_or_failed(self) -> None:
        """
        Awaits until the listener is canceled (on calling
        :meth:`~net.websockets.websocket_client.WebsocketClient.disconnect` method) or WebsocketClient fails with an
        exception.
        If :meth:`~net.websockets.websocket_client.WebsocketClient.connect` was never called or failure happened,
        this method returns immediately.
        Raises the original exception on failure.
        """
        if self._listen_failed is None:
            return
        await self._listen_failed
