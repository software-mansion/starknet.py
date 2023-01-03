import asyncio
from unittest.mock import MagicMock, patch

import pytest
from starkware.starknet.public.abi import get_storage_var_address

from starknet_py.net.client_errors import ClientError


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_node_get_declare_transaction_by_block_number_and_index(
    declare_transaction_hash, block_with_declare_number, full_node_client, class_hash
):
    tx = await full_node_client.get_transaction_by_block_id(
        block_number=block_with_declare_number, index=0
    )

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
async def test_state_update_full_node_client(
    full_node_client,
    block_with_declare_number,
    class_hash,
):
    state_update = await full_node_client.get_state_update(
        block_number=block_with_declare_number
    )

    assert class_hash in state_update.declared_contracts


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_storage_at_incorrect_address_full_node_client(full_node_client):
    with pytest.raises(ClientError, match="Contract not found"):
        await full_node_client.get_storage_at(
            contract_address=0x1111,
            key=get_storage_var_address("balance"),
            block_hash="latest",
        )
