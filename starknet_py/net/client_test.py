import pytest

from starknet_py.constants import ADDR_BOUND
from starknet_py.net.client_models import (
    DAMode,
    ResourceBoundsMapping,
    Transaction,
    TransactionV3,
)
from starknet_py.net.full_node_client import _to_storage_key
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
        _ = Transaction(hash=0, signature=[0, 0], version=0)


def test_cannot_instantiate_abstract_transaction_v3_class():
    with pytest.raises(
        TypeError, match="Cannot instantiate abstract TransactionV3 class."
    ):
        _ = TransactionV3(
            hash=0,
            signature=[0, 0],
            version=0,
            paymaster_data=[],
            tip=0,
            nonce_data_availability_mode=DAMode.L1,
            fee_data_availability_mode=DAMode.L1,
            resource_bounds=ResourceBoundsMapping.init_with_zeros(),
        )


def test_handle_rpc_error_server_error():
    no_error_dict = {"not_an_error": "success"}

    with pytest.raises(ServerError, match="RPC request failed."):
        RpcHttpClient.handle_rpc_error(no_error_dict)


@pytest.mark.parametrize(
    "key, expected",
    [
        (0x0, "0x00"),
        (0x12345, "0x012345"),
        (0x10001, "0x010001"),
        (0xFFAA, "0x00ffaa"),
        (0xDE, "0x00de"),
        (
            ADDR_BOUND - 1,
            "0x07fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeff",
        ),
    ],
)
def test_get_rpc_storage_key(key, expected):
    assert _to_storage_key(key) == expected


@pytest.mark.parametrize(
    "key",
    [int(1e100), -1, 0x8FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF],
)
def test_get_rpc_storage_key_raises_on_non_representable_key(key):
    with pytest.raises(ValueError, match="cannot be represented"):
        _to_storage_key(key)
