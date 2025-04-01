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
from starknet_py.net.websocket_client import WebsocketClient
from starknet_py.net.websocket_client_models import (  # ReorgData,; ReorgNotification,
    NewEventsNotification,
    NewHeadsNotification,
    NewTransactionStatus,
    PendingTransactionsNotification,
    ReorgData,
    ReorgNotification,
    Transaction,
    TransactionStatusNotification,
)
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_new_heads_subscription(
    websocket_client: WebsocketClient,
    devnet_client: DevnetClient,
):
    block_header_from_notification: Optional[BlockHeader] = None

    def handler(new_heads_notification: NewHeadsNotification):
        nonlocal block_header_from_notification
        block_header_from_notification = new_heads_notification.result

    subscription_id = await websocket_client.subscribe_new_heads(handler=handler)

    new_block_hash = await devnet_client.create_block()

    assert block_header_from_notification is not None
    assert int(new_block_hash, 16) == block_header_from_notification.block_hash

    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_new_events_subscription(
    websocket_client: WebsocketClient,
    deployed_balance_contract,
    argent_account_v040: BaseAccount,
):
    emitted_events: List[EmittedEvent] = []

    def handler(new_events_notification: NewEventsNotification):
        nonlocal emitted_events
        emitted_events.append(new_events_notification.result)

    subscription_id = await websocket_client.subscribe_events(
        handler=handler, from_address=argent_account_v040.address
    )

    value = 20
    increase_balance_by_20_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[value],
    )
    execute = await argent_account_v040.execute_v3(
        calls=increase_balance_by_20_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await argent_account_v040.client.wait_for_tx(tx_hash=execute.transaction_hash)
    await argent_account_v040.client.get_transaction_receipt(
        tx_hash=execute.transaction_hash
    )

    assert len(emitted_events) == 4
    for emitted_event in emitted_events:
        assert emitted_event.from_address == argent_account_v040.address

    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_transaction_status_subscription(
    websocket_client: WebsocketClient,
    deployed_balance_contract,
    argent_account_v040: BaseAccount,
):
    new_transaction_status: Optional[NewTransactionStatus] = None

    def handler(transaction_status_notification: TransactionStatusNotification):
        nonlocal new_transaction_status
        new_transaction_status = transaction_status_notification.result

    value = 20
    increase_balance_by_20_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[value],
    )
    execute = await argent_account_v040.execute_v3(
        calls=increase_balance_by_20_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    subscription_id = await websocket_client.subscribe_transaction_status(
        handler=handler, transaction_hash=execute.transaction_hash
    )

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

    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    assert unsubscribe_result is True


@pytest.mark.asyncio
@pytest.mark.skip
async def test_pending_transactions_subscription(
    websocket_client: WebsocketClient,
    deployed_balance_contract,
    argent_account_v040: BaseAccount,
):
    pending_transactions: List[Union[int, Transaction]] = []

    def handler(pending_transaction_notification: PendingTransactionsNotification):
        nonlocal pending_transactions
        pending_transactions.append(pending_transaction_notification.result)

    subscription_id = await websocket_client.subscribe_pending_transactions(
        handler=handler,
        sender_address=[argent_account_v040.address],
    )

    value = 20
    increase_balance_by_20_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[value],
    )
    execute = await argent_account_v040.execute_v3(
        calls=increase_balance_by_20_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    await argent_account_v040.client.wait_for_tx(tx_hash=execute.transaction_hash)
    await argent_account_v040.client.get_transaction_receipt(
        tx_hash=execute.transaction_hash
    )

    assert len(pending_transactions) == 1

    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_reorg_subscription(
    websocket_client: WebsocketClient,
    devnet_client: DevnetClient,
):
    reorg_data: Optional[ReorgData] = None

    def handler_new_heads(_new_heads_notification: NewHeadsNotification):
        pass

    def handler(reorg_notification: ReorgNotification):
        nonlocal reorg_data
        reorg_data = reorg_notification.result
        print("reorg_data", reorg_data)

    subscription_id = await websocket_client.subscribe_new_heads(
        handler=handler_new_heads
    )

    websocket_client.set_reorg_notification_handler(handler)

    new_block_hash = await devnet_client.create_block()

    await asyncio.sleep(10)

    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_unsubscribe_with_non_existing_id(
    websocket_client: WebsocketClient,
):
    unsubscribe_result = await websocket_client.unsubscribe(123)
    assert unsubscribe_result is False
