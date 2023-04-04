import asyncio
from unittest.mock import MagicMock, patch

import pytest

from starknet_py.contract import Contract
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.hash.storage import get_storage_var_address
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import DeclareTransaction


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_node_get_declare_transaction_by_block_number_and_index(
        declare_transaction_hash, block_with_declare_number, full_node_client, class_hash
):
    tx = await full_node_client.get_transaction_by_block_id(
        block_number=block_with_declare_number, index=0
    )

    assert isinstance(tx, DeclareTransaction)
    assert tx.hash == declare_transaction_hash
    assert tx.class_hash == class_hash
    assert tx.version == 1


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_class_at(full_node_client, contract_address):
    declared_contract = await full_node_client.get_class_at(
        contract_address=contract_address, block_hash="latest"
    )

    assert declared_contract.program != {}
    assert declared_contract.entry_points_by_type is not None
    assert declared_contract.abi is not None


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_class_at_throws_on_wrong_address(full_node_client):
    with pytest.raises(
            ClientError, match="Client failed with code 20: Contract not found."
    ):
        await full_node_client.get_class_at(contract_address=0, block_hash="latest")


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_block_transaction_count(full_node_client):
    latest_block = await full_node_client.get_block("latest")

    for block_number in range(1, latest_block.block_number + 1):
        transaction_count = await full_node_client.get_block_transaction_count(
            block_number=block_number
        )

        assert transaction_count == 1


@pytest.mark.asyncio
async def test_method_raises_on_both_block_hash_and_number(full_node_client):
    with pytest.raises(
            ValueError,
            match="Arguments block_hash and block_number are mutually exclusive.",
    ):
        await full_node_client.get_block(block_number=0, block_hash="0x0")


@pytest.mark.asyncio
async def test_pending_transactions(full_node_client):
    with patch(
            "starknet_py.net.http_client.RpcHttpClient.call", MagicMock()
    ) as mocked_http_call:
        result = asyncio.Future()
        result.set_result(
            [
                {
                    "transaction_hash": "0x01",
                    "class_hash": "0x05",
                    "version": "0x0",
                    "type": "DEPLOY",
                    "contract_address": "0x02",
                    "contract_address_salt": "0x0",
                    "constructor_calldata": [],
                }
            ]
        )
        mocked_http_call.return_value = result

        pending_transactions = await full_node_client.get_pending_transactions()

        assert len(pending_transactions) == 1
        assert pending_transactions[0].hash == 0x1
        assert pending_transactions[0].signature == []
        assert pending_transactions[0].max_fee == 0


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_storage_at_incorrect_address_full_node_client(full_node_client):
    with pytest.raises(ClientError, match="Contract not found"):
        await full_node_client.get_storage_at(
            contract_address=0x1111,
            key=get_storage_var_address("balance"),
            block_hash="latest",
        )


# TODO FIX TESTS BELOW AFTER DEVNET FIX REGARDING CONTINUATION_TOKEN
# more about in /starknet_py/net/full_node_client.py:162

def _parse_event_name(event: str) -> str:
    from starknet_py.net.full_node_client import _to_rpc_felt
    return _to_rpc_felt(get_selector_from_name(event))
    # return get_selector_from_name(event)


FUNCTION_ONE_NAME = "put"
EVENT_ONE_PARSED_NAME = _parse_event_name("put_called")
FUNCTION_TWO_NAME = "another_put"
EVENT_TWO_PARSED_NAME = _parse_event_name("another_put_called")


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_with_single_event_no_continuation_token(
        full_node_client,
        simple_storage_with_event_contract: Contract,
):
    for i in range(1, 4):
        await simple_storage_with_event_contract.functions[FUNCTION_ONE_NAME].invoke(
            i, i, auto_estimate=True
        )
    events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[EVENT_ONE_PARSED_NAME],
        follow_continuation_token=False,
        chunk_size=3,
    )
    assert len(events_response.events) == 3
    assert events_response.continuation_token is not None


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_with_single_event_with_continuation_token(
        full_node_client,
        simple_storage_with_event_contract: Contract,
):
    await simple_storage_with_event_contract.functions[FUNCTION_ONE_NAME].invoke(
        7, 14, auto_estimate=True
    )
    await simple_storage_with_event_contract.functions[FUNCTION_ONE_NAME].invoke(
        22, 44, auto_estimate=True
    )
    events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[EVENT_ONE_PARSED_NAME],
        follow_continuation_token=True,
        chunk_size=1,
    )
    assert len(events_response.events) == 2
    # TODO
    # assert events_response.continuation_token is None


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_with_single_event_nonexistent_event_name(
        full_node_client,
        simple_storage_with_event_contract: Contract,
):
    await simple_storage_with_event_contract.functions[FUNCTION_ONE_NAME].invoke(
        1, 1, auto_estimate=True
    )
    events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=["nonexistent_event"],
        follow_continuation_token=False,
        chunk_size=3,
    )
    assert len(events_response.events) == 0
    # TODO
    # assert events_response.continuation_token is None


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_with_two_events(
        full_node_client,
        simple_storage_with_event_contract: Contract,
):
    await simple_storage_with_event_contract.functions[FUNCTION_ONE_NAME].invoke(
        1, 1, auto_estimate=True
    )
    await simple_storage_with_event_contract.functions[FUNCTION_TWO_NAME].invoke(
        2, 2, auto_estimate=True
    )
    await simple_storage_with_event_contract.functions[FUNCTION_TWO_NAME].invoke(
        3, 3, auto_estimate=True
    )
    event_one_events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[EVENT_ONE_PARSED_NAME],
        follow_continuation_token=True,
    )
    event_two_events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[EVENT_TWO_PARSED_NAME],
        follow_continuation_token=True,
    )
    event_one_two_events_response = await full_node_client.get_events(
        from_block_number=0,
        to_block_hash="latest",
        address=simple_storage_with_event_contract.address,
        keys=[EVENT_TWO_PARSED_NAME, EVENT_ONE_PARSED_NAME],
        follow_continuation_token=True,
    )
    assert len(event_one_events_response.events) == 1
    # TODO
    # assert events_response.continuation_token is None
    assert len(event_two_events_response.events) == 2
    # TODO
    # assert event_two_events_response.continuation_token is None
    assert len(event_one_two_events_response.events) == 3


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_events_nonexistent_starting_block(
        full_node_client,
        simple_storage_with_event_contract: Contract,
):
    with pytest.raises(ClientError, match="Block not found"):
        await full_node_client.get_events(
            from_block_number=10000,
            to_block_hash="latest",
            address=simple_storage_with_event_contract.address,
            keys=[EVENT_ONE_PARSED_NAME],
            follow_continuation_token=False,
            chunk_size=1,
        )
