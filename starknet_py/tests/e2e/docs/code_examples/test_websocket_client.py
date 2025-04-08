# pylint: disable=import-outside-toplevel
import asyncio
from typing import List, Optional, Union

import pytest

from starknet_py.devnet_utils.devnet_client import DevnetClient
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client_models import (
    BlockHeader,
    Call,
    EmittedEvent,
    TransactionExecutionStatus,
    TransactionStatus,
)
from starknet_py.net.models import StarknetChainId
from starknet_py.net.websockets.models import (
    NewTransactionStatus,
    ReorgData,
    Transaction,
)
from starknet_py.net.websockets.websocket_client import WebsocketClient
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_connect_and_disconnect(devnet_ws: str):
    # pylint: disable=unused-variable
    # pylint: disable=redefined-outer-name
    # pylint: disable=reimported
    # docs-start: connect
    from starknet_py.net.websockets.websocket_client import WebsocketClient

    # Create `WebsocketClient` instance
    websocket_client = WebsocketClient("wss://your.node.url")
    # docs-end: connect
    websocket_client = WebsocketClient(devnet_ws)
    assert not await websocket_client.is_connected

    # docs-start: connect

    # Connect to the websocket server
    await websocket_client.connect()
    # docs-end: connect
    assert await websocket_client.is_connected

    # docs-start: disconnect
    # Disconnect from the websocket server
    await websocket_client.disconnect()
    # docs-end: disconnect
    assert not await websocket_client.is_connected


@pytest.mark.asyncio
async def test_subscribe_new_heads(
    websocket_client: WebsocketClient,
    devnet_client: DevnetClient,
):
    received_block: Optional[BlockHeader] = None

    # docs-start: subscribe_new_heads
    from starknet_py.net.websockets.models import NewHeadsNotification

    # Create a handler function that will be called when a new block is created
    def handler(new_heads_notification: NewHeadsNotification):
        # Perform the necessary actions with the new block...

        # docs-end: subscribe_new_heads
        nonlocal received_block
        received_block = new_heads_notification.result

    # docs-start: subscribe_new_heads
    # Subscribe to new heads notifications
    subscription_id = await websocket_client.subscribe_new_heads(handler=handler)

    # Here you can put code which will keep the application running (e.g. using loop and `asyncio.sleep`)
    # ...
    # docs-end: subscribe_new_heads
    new_block_hash = await devnet_client.create_block()

    assert received_block is not None
    assert int(new_block_hash, 16) == received_block.block_hash
    # docs-start: subscribe_new_heads

    # Unsubscribe from the notifications
    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    # docs-end: subscribe_new_heads
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_subscribe_events(
    websocket_client: WebsocketClient,
    deployed_balance_contract,
    argent_account_v040: BaseAccount,
):
    account = argent_account_v040
    emitted_events: List[EmittedEvent] = []

    # docs-start: subscribe_events
    from starknet_py.net.websockets.models import NewEventsNotification

    # Create a handler function that will be called when a new event is emitted
    def handler(new_events_notification: NewEventsNotification):
        # Perform the necessary actions with the new event...

        # docs-end: subscribe_events
        nonlocal emitted_events
        emitted_events.append(new_events_notification.result)

    # docs-start: subscribe_events
    # Subscribe to new events notifications
    subscription_id = await websocket_client.subscribe_events(
        handler=handler, from_address=account.address
    )

    # Here you can put code which will keep the application running (e.g. using loop and `asyncio.sleep`)
    # ...
    # docs-end: subscribe_events
    increase_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )
    execute = await argent_account_v040.execute_v3(
        calls=increase_balance_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await argent_account_v040.client.wait_for_tx(tx_hash=execute.transaction_hash)
    await argent_account_v040.client.get_transaction_receipt(
        tx_hash=execute.transaction_hash
    )

    assert len(emitted_events) > 0
    for emitted_event in emitted_events:
        assert emitted_event.from_address == account.address
    # docs-start: subscribe_events

    # Unsubscribe from the notifications
    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    # docs-end: subscribe_events
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_subscribe_transaction_status(
    websocket_client: WebsocketClient,
    deployed_balance_contract,
    argent_account_v040: BaseAccount,
):
    new_transaction_status: Optional[NewTransactionStatus] = None

    # docs-start: subscribe_transaction_status
    from starknet_py.net.websockets.models import TransactionStatusNotification

    # Create a handler function that will be called when a new transaction status is emitted
    def handler(transaction_status_notification: TransactionStatusNotification):
        # Perform the necessary actions with the new transaction status...

        # docs-end: subscribe_transaction_status
        nonlocal new_transaction_status
        new_transaction_status = transaction_status_notification.result

    increase_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )
    execute = await argent_account_v040.execute_v3(
        calls=increase_balance_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    # docs-start: subscribe_transaction_status
    # Subscribe to transaction status notifications
    subscription_id = await websocket_client.subscribe_transaction_status(
        handler=handler, transaction_hash=execute.transaction_hash
    )

    # Here you can put code which will keep the application running (e.g. using loop and `asyncio.sleep`)
    # ...
    # docs-end: subscribe_transaction_status
    await argent_account_v040.client.wait_for_tx(tx_hash=execute.transaction_hash)
    await argent_account_v040.client.get_transaction_receipt(
        tx_hash=execute.transaction_hash
    )

    await asyncio.sleep(10)

    assert new_transaction_status is not None
    assert new_transaction_status.transaction_hash == execute.transaction_hash
    assert (
        new_transaction_status.status.finality_status
        == TransactionStatus.ACCEPTED_ON_L2
    )
    assert (
        new_transaction_status.status.execution_status
        == TransactionExecutionStatus.SUCCEEDED
    )
    assert new_transaction_status.status.failure_reason is None

    # docs-start: subscribe_transaction_status

    # Unsubscribe from the notifications
    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    # docs-end: subscribe_transaction_status
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_subscribe_pending_transactions(
    websocket_client: WebsocketClient,
    deployed_balance_contract,
    argent_account_v040: BaseAccount,
):
    account = argent_account_v040
    pending_transactions: List[Union[int, Transaction]] = []

    # docs-start: subscribe_pending_transactions
    from starknet_py.net.websockets.models import PendingTransactionsNotification

    # Create a handler function that will be called when a new pending transaction is emitted
    def handler(pending_transaction_notification: PendingTransactionsNotification):
        # Perform the necessary actions with the new pending transaction...

        # docs-end: subscribe_pending_transactions
        nonlocal pending_transactions
        pending_transactions.append(pending_transaction_notification.result)

    # docs-start: subscribe_pending_transactions
    # Subscribe to pending transactions notifications
    subscription_id = await websocket_client.subscribe_pending_transactions(
        handler=handler,
        sender_address=[account.address],
    )

    # Here you can put code which will keep the application running (e.g. using loop and `asyncio.sleep`)
    # ...
    # docs-end: subscribe_pending_transactions
    increase_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )
    execute = await argent_account_v040.execute_v3(
        calls=increase_balance_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    await argent_account_v040.client.wait_for_tx(tx_hash=execute.transaction_hash)
    await argent_account_v040.client.get_transaction_receipt(
        tx_hash=execute.transaction_hash
    )

    assert len(pending_transactions) == 1
    pending_transaction = pending_transactions[0]

    transaction_hash = (
        execute.transaction_hash
        if isinstance(pending_transaction, int)
        else pending_transaction.calculate_hash(StarknetChainId.SEPOLIA)
    )
    assert execute.transaction_hash == transaction_hash

    # docs-start: subscribe_pending_transactions

    # Unsubscribe from the notifications
    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    # docs-end: subscribe_pending_transactions
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_on_chain_reorg(
    websocket_client: WebsocketClient,
    devnet_client: DevnetClient,
):
    reorg_data: Optional[ReorgData] = None

    # docs-start: on_chain_reorg
    from starknet_py.net.websockets.models import ReorgNotification

    # Create a handler function that will be called when a reorg notification is emitted
    def handler_reorg(reorg_notification: ReorgNotification):
        # Perform the necessary actions with the reorg data...

        # docs-end: on_chain_reorg
        nonlocal reorg_data
        reorg_data = reorg_notification.result

    # docs-start: on_chain_reorg
    # Set the handler function for reorg notifications
    websocket_client.on_chain_reorg = handler_reorg

    # Subscribe to new heads, events, or transaction status notifications.
    # In this example we will subscribe to new heads notifications.
    # Note: we're passing empty handler function here, as we're only interested in reorg notifications.
    subscription_id = await websocket_client.subscribe_new_heads(handler=lambda _: _)

    # Here you can put code which will keep the application running (e.g. using loop and `asyncio.sleep`)
    # ...
    # docs-end: on_chain_reorg
    new_block_hash = await devnet_client.create_block()

    await devnet_client.abort_block(block_hash=new_block_hash)

    await asyncio.sleep(5)

    assert reorg_data is not None
    assert reorg_data.starting_block_hash == int(new_block_hash, 16)
    assert reorg_data.ending_block_hash == int(new_block_hash, 16)

    # docs-start: on_chain_reorg

    # Unsubscribe from the notifications
    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    # docs-end: on_chain_reorg
    assert unsubscribe_result is True
