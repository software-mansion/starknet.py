import pytest

from starknet_py.net.client_models import Transaction
from starknet_py.net.http_client import RpcHttpClient, ServerError


@pytest.mark.asyncio
async def test_wait_for_tx_negative_check_interval(client):
    with pytest.raises(
        ValueError, match="Argument check_interval has to be greater than 0."
    ):
        await client.wait_for_tx(tx_hash=0, check_interval=-1)


def test_cannot_instantiate_abstract_transaction_class():
    with pytest.raises(
        TypeError, match="Cannot instantiate abstract Transaction class."
    ):
        _ = Transaction(hash=0, signature=[0, 0], max_fee=0, version=0)


def test_handle_rpc_error_server_error():
    no_error_dict = {"not_an_error": "success"}

    with pytest.raises(ServerError, match="RPC request failed."):
        RpcHttpClient.handle_rpc_error(no_error_dict)
