from unittest.mock import AsyncMock, patch

import pytest

from starknet_py.net.tip import estimate_tip
from starknet_py.tests.e2e.fixtures.misc import (
    starknet_block_mock,
    transaction_mock_with_tip,
)


@pytest.mark.asyncio
async def test_tip(get_block_with_txs_path, client):
    with patch(get_block_with_txs_path, AsyncMock()) as get_block_with_txs_mock:
        block = starknet_block_mock()
        block.transactions = [
            transaction_mock_with_tip(10),
            transaction_mock_with_tip(20),
            transaction_mock_with_tip(30),
        ]
        get_block_with_txs_mock.return_value = block

        assert await estimate_tip(client) == 20


@pytest.mark.asyncio
async def test_tip_no_txs(get_block_with_txs_path, client):
    with patch(get_block_with_txs_path, AsyncMock()) as get_block_with_txs_mock:
        block = starknet_block_mock()
        block.transactions = []
        get_block_with_txs_mock.return_value = block

        assert await estimate_tip(client) == 0


@pytest.mark.asyncio
async def test_tip_all_equal(get_block_with_txs_path, client):
    with patch(get_block_with_txs_path, AsyncMock()) as get_block_with_txs_mock:
        block = starknet_block_mock()
        block.transactions = [
            transaction_mock_with_tip(10),
            transaction_mock_with_tip(10),
            transaction_mock_with_tip(10),
        ]
        get_block_with_txs_mock.return_value = block

        assert await estimate_tip(client) == 10


@pytest.mark.asyncio
async def test_tip_even(get_block_with_txs_path, client):
    with patch(get_block_with_txs_path, AsyncMock()) as get_block_with_txs_mock:
        block = starknet_block_mock()
        block.transactions = [
            transaction_mock_with_tip(10),
            transaction_mock_with_tip(20),
            transaction_mock_with_tip(30),
            transaction_mock_with_tip(40),
        ]
        get_block_with_txs_mock.return_value = block

        assert await estimate_tip(client) == 25


@pytest.mark.asyncio
async def test_tip_zeroes(get_block_with_txs_path, client):
    with patch(get_block_with_txs_path, AsyncMock()) as get_block_with_txs_mock:
        block = starknet_block_mock()
        block.transactions = [
            transaction_mock_with_tip(0),
            transaction_mock_with_tip(0),
            transaction_mock_with_tip(30),
            transaction_mock_with_tip(40),
        ]
        get_block_with_txs_mock.return_value = block

        assert await estimate_tip(client) == 15


@pytest.mark.asyncio
async def test_tip_all_zeroes(get_block_with_txs_path, client):
    with patch(get_block_with_txs_path, AsyncMock()) as get_block_with_txs_mock:
        block = starknet_block_mock()
        block.transactions = [
            transaction_mock_with_tip(0),
            transaction_mock_with_tip(0),
        ]
        get_block_with_txs_mock.return_value = block

        assert await estimate_tip(client) == 0
