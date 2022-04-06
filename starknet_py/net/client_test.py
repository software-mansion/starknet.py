from asyncio import Future
from unittest.mock import MagicMock

import pytest


from starkware.starknet.services.api.feeder_gateway.response_objects import (
    TransactionStatus,
)

from starknet_py.net.client import Client
from starknet_py.transaction_exceptions import (
    TransactionRejectedException,
    TransactionNotReceivedException,
    TransactionFailedException,
)


@pytest.mark.asyncio
async def test_wait_for_tx_throws_transaction_rejected():
    client = Client("testnet")

    result = Future()
    result.set_result(MagicMock(status=TransactionStatus.REJECTED))
    client.get_transaction = MagicMock()
    client.get_transaction.return_value = result

    with pytest.raises(TransactionRejectedException):
        await client.wait_for_tx(tx_hash="0x0")


@pytest.mark.asyncio
async def test_wait_for_tx_throws_transaction_not_received():
    client = Client("testnet")

    result = Future()
    result.set_result(MagicMock(status=TransactionStatus.NOT_RECEIVED))
    client.get_transaction = MagicMock()
    client.get_transaction.return_value = result

    with pytest.raises(TransactionNotReceivedException):
        await client.wait_for_tx(tx_hash="0x0")


@pytest.mark.asyncio
async def test_wait_for_tx_throws_transaction_failed():
    client = Client("testnet")

    result = Future()
    # TransactionStatus is and Enum, using nonsensical value to test for base exception
    result.set_result(MagicMock(status=-100))
    client.get_transaction = MagicMock()
    client.get_transaction.return_value = result

    with pytest.raises(TransactionFailedException):
        await client.wait_for_tx(tx_hash="0x0")
