from asyncio import Future
from unittest.mock import MagicMock

import pytest


from starkware.starknet.services.api.feeder_gateway.response_objects import (
    TransactionStatus,
    TransactionFailureReason,
)

from starknet_py.net.client import Client
from starknet_py.transaction_exceptions import (
    TransactionRejectedError,
    TransactionNotReceivedError,
    TransactionFailedError,
)


@pytest.mark.asyncio
async def test_wait_for_tx_throws_transaction_rejected():
    client = Client("testnet")
    code = "TRANSACTION REJECTED"
    message = "Transaction was rejected"

    result = Future()
    # noinspection PyArgumentList
    result.set_result(
        MagicMock(
            status=TransactionStatus.REJECTED,
            transaction_failure_reason=TransactionFailureReason(
                code=code, error_message=message
            ),
        )
    )
    client.get_transaction = MagicMock()
    client.get_transaction.return_value = result

    with pytest.raises(TransactionRejectedError) as exinfo:
        await client.wait_for_tx(tx_hash="0x0")

    assert exinfo.value.code == code
    assert exinfo.value.message == message


@pytest.mark.asyncio
async def test_wait_for_tx_throws_transaction_not_received():
    client = Client("testnet")

    result = Future()
    result.set_result(MagicMock(status=TransactionStatus.NOT_RECEIVED))
    client.get_transaction = MagicMock()
    client.get_transaction.return_value = result

    with pytest.raises(TransactionNotReceivedError):
        await client.wait_for_tx(tx_hash="0x0")


@pytest.mark.asyncio
async def test_wait_for_tx_throws_transaction_failed():
    client = Client("testnet")

    result = Future()
    # TransactionStatus is and Enum, using nonsensical value to test for base exception
    result.set_result(MagicMock(status=-100))
    client.get_transaction = MagicMock()
    client.get_transaction.return_value = result

    with pytest.raises(TransactionFailedError):
        await client.wait_for_tx(tx_hash="0x0")
