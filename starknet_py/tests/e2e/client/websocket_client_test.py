from typing import Optional

import pytest

from starknet_py.devnet_utils.devnet_client import DevnetClient
from starknet_py.net.client_models import BlockHeader, StarknetBlock
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.websockets.errors import WebsocketClientError
from starknet_py.net.websockets.models import NewHeadsNotification
from starknet_py.net.websockets.websocket_client import WebsocketClient


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
