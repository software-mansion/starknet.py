from typing import Tuple

import pytest

from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.tests.e2e.utils import DevnetClientFactory
from starknet_py.net.base_client import BaseClient
from starknet_py.net.client_models import (
    TransactionType,
    TransactionStatus,
    InvokeFunction,
)


@pytest.mark.asyncio
async def test_get_transaction(clients, deploy_transaction_hash, contract_address):
    for client in clients:
        transaction = await client.get_transaction(deploy_transaction_hash)

        assert transaction.contract_address == contract_address
        assert transaction.calldata == []
        assert transaction.entry_point_selector == 0
        assert transaction.transaction_type == TransactionType.DEPLOY


@pytest.mark.asyncio
async def test_get_block(clients, deploy_transaction_hash):
    for client in clients:
        block = await client.get_block(block_number=0)

        assert block.block_number == 0
        assert any(i.hash == deploy_transaction_hash for i in block.transactions)


@pytest.mark.asyncio
async def test_get_storage_at(clients, block_hash, contract_address):
    for client in clients:
        storage = await client.get_storage_at(
            contract_address=contract_address,
            key=916907772491729262376534102982219947830828984996257231353398618781993312401,
            block_hash=block_hash,
        )

        assert storage == 1234


@pytest.mark.asyncio
async def test_get_storage_at_incorrect_address(clients, block_hash):
    for client in clients:
        storage = await client.get_storage_at(
            contract_address=0x1111,
            key=916907772491729262376534102982219947830828984996257231353398618781993312401,
            block_hash=block_hash,
        )

        assert storage == 0


@pytest.mark.asyncio
async def test_get_transaction_receipt(clients, invoke_transaction_hash):
    for client in clients:
        receipt = await client.get_transaction_receipt(tx_hash=invoke_transaction_hash)

        assert receipt.hash == invoke_transaction_hash
        assert receipt.status in (
            TransactionStatus.ACCEPTED_ON_L1,
            TransactionStatus.ACCEPTED_ON_L2,
        )


@pytest.mark.asyncio
async def test_get_code(clients, contract_address):
    for client in clients:
        code = await client.get_code(contract_address=contract_address)

        assert code.abi is not None
        assert len(code.abi) != 0
        assert code.bytecode is not None
        assert len(code.bytecode) != 0


@pytest.mark.asyncio
async def test_estimate_fee(devnet_address, contract_address):
    client = await DevnetClientFactory(
        devnet_address
    ).make_devnet_client_without_account()
    transaction = InvokeFunction(
        contract_address=contract_address,
        entry_point_selector=get_selector_from_name("increase_balance"),
        calldata=[123],
        max_fee=0,
        version=0,
        signature=[0x0, 0x0],
    )
    estimate_fee = await client.estimate_fee(tx=transaction)

    assert estimate_fee is not None
    assert isinstance(estimate_fee, int)


@pytest.mark.asyncio
async def test_call_contract(clients, contract_address):
    for client in clients:
        invoke_function = InvokeFunction(
            contract_address=contract_address,
            entry_point_selector=get_selector_from_name("get_balance"),
            calldata=[],
            max_fee=0,
            version=0,
            signature=[0x0, 0x0],
        )
        result = await client.call_contract(invoke_function, block_hash="latest")

        assert result == [1234]


@pytest.mark.asyncio
async def test_add_transaction(devnet_address, contract_address):
    client = await DevnetClientFactory(
        devnet_address
    ).make_devnet_client_without_account()
    invoke_function = InvokeFunction(
        contract_address=contract_address,
        entry_point_selector=get_selector_from_name("increase_balance"),
        calldata=[0],
        max_fee=0,
        version=0,
        signature=[0x0, 0x0],
    )
    result = await client.add_transaction(invoke_function)

    assert result.address == contract_address
    assert result.code == "TRANSACTION_RECEIVED"


@pytest.mark.asyncio
async def test_deploy(devnet_address, balance_contract):
    client = await DevnetClientFactory(
        devnet_address
    ).make_devnet_client_without_account()
    result = await client.deploy(contract=balance_contract, constructor_calldata=[])

    assert result.code == "TRANSACTION_RECEIVED"
