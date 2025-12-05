import asyncio
from json import JSONDecodeError
from typing import List, Optional
from unittest.mock import patch

import marshmallow
import pytest

from starknet_py.devnet_utils.devnet_client import DevnetClient
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client_models import (
    BlockHeader,
    Call,
    EmittedEventWithFinalityStatus,
    StarknetBlock,
    TransactionFinalityStatus,
    TransactionFinalityStatusWithoutL1,
    TransactionReceipt,
    TransactionStatusWithoutL1,
)
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.websockets.errors import WebsocketClientError
from starknet_py.net.websockets.models import (
    NewEventsNotification,
    NewHeadsNotification,
    NewTransactionNotification,
    NewTransactionNotificationResult,
    NewTransactionReceiptsNotification,
)
from starknet_py.net.websockets.websocket_client import WebsocketClient
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_subscribe_new_heads_with_block_hash(
    client: FullNodeClient,
    websocket_client: WebsocketClient,
    devnet_client: DevnetClient,
):
    received_block: Optional[BlockHeader] = None

    def handler(new_heads_notification: NewHeadsNotification):
        nonlocal received_block
        received_block = new_heads_notification.result

    latest_block = await client.get_block(block_hash="latest")
    assert isinstance(latest_block, StarknetBlock)

    subscription_id = await websocket_client.subscribe_new_heads(
        handler=handler, block_hash=latest_block.block_hash
    )

    new_block_hash = await devnet_client.create_block()
    await asyncio.sleep(5)

    assert received_block is not None
    assert int(new_block_hash, 16) == received_block.block_hash

    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_subscribe_new_heads_with_block_number(
    client: FullNodeClient,
    websocket_client: WebsocketClient,
    devnet_client: DevnetClient,
):
    received_block: Optional[BlockHeader] = None

    def handler(new_heads_notification: NewHeadsNotification):
        nonlocal received_block
        received_block = new_heads_notification.result

    latest_block = await client.get_block(block_hash="latest")
    assert isinstance(latest_block, StarknetBlock)

    subscription_id = await websocket_client.subscribe_new_heads(
        handler=handler, block_number=latest_block.block_number
    )

    new_block_hash = await devnet_client.create_block()
    await asyncio.sleep(5)

    assert received_block is not None
    assert int(new_block_hash, 16) == received_block.block_hash

    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_subscribe_new_heads_with_both_block_params_passed(
    websocket_client: WebsocketClient,
):
    with pytest.raises(
        ValueError,
        match="Arguments block_hash and block_number are mutually exclusive.",
    ):
        await websocket_client.subscribe_new_heads(
            handler=lambda _: _, block_hash=1, block_number=1
        )


@pytest.mark.asyncio
async def test_subscribe_new_heads_too_many_blocks_back(
    websocket_client: WebsocketClient,
    devnet_client_fork_mode: DevnetClient,
):
    client = FullNodeClient(devnet_client_fork_mode.url)
    latest_block = await client.get_block(block_hash="latest")

    assert isinstance(latest_block, StarknetBlock)
    assert latest_block.block_number >= 1025

    # TODO(#1574): Change error to `TOO_MANY_BLOCKS_BACK` once devnet issue is resolved.
    query_block_number = latest_block.block_number - 1025
    with pytest.raises(
        WebsocketClientError,
        match="WebsocketClient failed with code 24. Message: Block not found.",
    ):
        await websocket_client.subscribe_new_heads(
            handler=lambda _: _, block_number=query_block_number
        )


@pytest.mark.asyncio
async def test_unsubscribe_with_non_existing_id(
    websocket_client: WebsocketClient,
):
    unsubscribe_result = await websocket_client.unsubscribe("123")
    assert unsubscribe_result is False


@pytest.mark.asyncio
async def test_subscribe_events_with_finality_status(
    websocket_client: WebsocketClient,
    deployed_balance_contract,
    argent_account_v040: BaseAccount,
):
    received_events: List = []

    def handler(new_events_notification: NewEventsNotification):
        nonlocal received_events
        received_events.append(new_events_notification.result)

    subscription_id = await websocket_client.subscribe_events(
        handler=handler,
        # We subscribe to the events from the account because it emits them for each executed transaction.
        # Balance contract doesn't emit anything.
        from_address=argent_account_v040.address,
        finality_status=TransactionFinalityStatusWithoutL1.ACCEPTED_ON_L2,
    )

    increase_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )
    execute = await argent_account_v040.execute_v3(
        calls=increase_balance_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    await argent_account_v040.client.wait_for_tx(tx_hash=execute.transaction_hash)
    await asyncio.sleep(3)

    assert len(received_events) >= 1
    assert all(
        ev.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2
        for ev in received_events
    )

    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_subscribe_new_transactions_with_finality_status(
    websocket_client: WebsocketClient,
    deployed_balance_contract,
    argent_account_v040: BaseAccount,
):
    received: List[NewTransactionNotificationResult] = []

    def handler(new_tx_notification: NewTransactionNotification):
        nonlocal received
        received.append(new_tx_notification.result)

    subscription_id = await websocket_client.subscribe_new_transactions(
        handler=handler,
        sender_address=[argent_account_v040.address],
        finality_status=[TransactionStatusWithoutL1.ACCEPTED_ON_L2],
    )

    increase_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )
    execute = await argent_account_v040.execute_v3(
        calls=increase_balance_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    await argent_account_v040.client.wait_for_tx(tx_hash=execute.transaction_hash)
    await asyncio.sleep(3)

    assert len(received) >= 1
    assert all(
        r.finality_status == TransactionStatusWithoutL1.ACCEPTED_ON_L2 for r in received
    )

    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_subscribe_new_transaction_receipts_with_finality_status(
    websocket_client: WebsocketClient,
    deployed_balance_contract,
    argent_account_v040: BaseAccount,
):
    receipts: List[TransactionReceipt] = []

    def handler(new_tx_receipt: NewTransactionReceiptsNotification):
        nonlocal receipts
        receipts.append(new_tx_receipt.result)

    subscription_id = await websocket_client.subscribe_new_transaction_receipts(
        handler=handler,
        sender_address=[argent_account_v040.address],
        finality_status=[TransactionFinalityStatusWithoutL1.ACCEPTED_ON_L2],
    )

    increase_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )
    execute = await argent_account_v040.execute_v3(
        calls=increase_balance_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    await argent_account_v040.client.wait_for_tx(tx_hash=execute.transaction_hash)
    await asyncio.sleep(10)

    assert len(receipts) >= 1
    assert all(
        r.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2 for r in receipts
    )

    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_subscribe_events_with_all_filters(
    client: FullNodeClient,
    websocket_client: WebsocketClient,
    deployed_balance_contract,
    argent_account_v040: BaseAccount,
):
    received_events: List[EmittedEventWithFinalityStatus] = []

    def handler(new_events_notification: NewEventsNotification):
        nonlocal received_events
        received_events.append(new_events_notification.result)

    latest_block = await client.get_block(block_hash="latest")
    assert isinstance(latest_block, StarknetBlock)

    subscription_id = await websocket_client.subscribe_events(
        handler=handler,
        from_address=argent_account_v040.address,
        keys=[[]],
        block_number=latest_block.block_number,
        finality_status=TransactionFinalityStatusWithoutL1.ACCEPTED_ON_L2,
    )

    increase_balance_call = Call(
        to_addr=deployed_balance_contract.address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )
    execute = await argent_account_v040.execute_v3(
        calls=increase_balance_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )

    await argent_account_v040.client.wait_for_tx(tx_hash=execute.transaction_hash)
    await asyncio.sleep(3)

    assert len(received_events) >= 1
    assert all(
        ev.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2
        for ev in received_events
    )
    assert received_events[0].from_address == argent_account_v040.address

    execute_receipt = await client.get_transaction_receipt(execute.transaction_hash)
    assert received_events[0].block_number is not None
    assert received_events[0].block_number + 1 == execute_receipt.block_number

    unsubscribe_result = await websocket_client.unsubscribe(subscription_id)
    assert unsubscribe_result is True


@pytest.mark.asyncio
async def test_subscribe_failure():
    # pylint: disable=no-self-use
    class FakeConnection:
        async def recv(self):
            return "xyz"

        # pylint: disable=unused-argument
        async def send(self, *args, **kwargs):
            return

        async def close(self):
            return

    async def fake_connect(*_args, **_kwargs):
        return FakeConnection()

    with patch(
        "starknet_py.net.websockets.websocket_client.connect", side_effect=fake_connect
    ):
        ws = WebsocketClient("wss://example.invalid")
        await ws.connect()

        with pytest.raises(JSONDecodeError):
            await ws.subscribe_events(lambda _: None)

        await ws.disconnect()


@pytest.mark.asyncio
async def test_listener_failure():
    # pylint: disable=no-self-use
    class FakeConnection:
        async def recv(self):
            # pylint: disable=line-too-long
            return '{"method": "starknet_subscriptionNewTransactionReceipts","params": {"subscription_id": "1234", "result": {"unknown_key": 12345}}}'

        async def send(self):
            return

        async def close(self):
            return

    async def fake_connect(*_args, **_kwargs):
        return FakeConnection()

    with patch(
        "starknet_py.net.websockets.websocket_client.connect", side_effect=fake_connect
    ):
        ws = WebsocketClient("wss://example.invalid")
        await ws.connect()

        # pylint: disable=protected-access
        ws._subscriptions["1234"] = lambda _: None

        with pytest.raises(marshmallow.ValidationError):
            await ws.wait_closed_or_failed()

        await ws.disconnect()
