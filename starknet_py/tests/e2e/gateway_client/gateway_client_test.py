import pytest

from starknet_py.tests.e2e.gateway_client.balance_contract import BALANCE_CONTRACT
from starknet_py.tests.e2e.utils import DevnetClientWithoutAccount, DevnetClientRpc
from starknet_py.net.client_models import (
    TransactionType,
    TransactionStatus,
    InvokeFunction,
)
from starknet_py.net.base_client import BaseClient


from starkware.starknet.public.abi import get_selector_from_name

DEPLOY_TRANSACTION_HASH = (
    0x11C1C6731ACE34AB4A9137A82092F26ECE38E7428E5E2028DA587893AAE0E02
)
INVOKE_TRANSACTION_HASH = (
    0x5A8995AE36F3A87CC217311EC9372CD16602BA0FC273F4AFD1508A627D81B30
)
CONTRACT_ADDRESS = 0x043D95E049C7DECE86574A8D3FB5C0F9E4422F8A7FEC6D744F26006374642252


@pytest.mark.asyncio
async def test_get_transaction():
    client = DevnetClientWithoutAccount()
    transaction = await client.get_transaction(DEPLOY_TRANSACTION_HASH)

    assert transaction.contract_address == CONTRACT_ADDRESS
    assert transaction.calldata == []
    assert transaction.entry_point_selector == 0
    assert transaction.transaction_type == TransactionType.DEPLOY


@pytest.mark.asyncio
async def test_get_block():
    client = DevnetClientWithoutAccount()
    block = await client.get_block(block_number=0)

    assert block.block_number == 0
    assert any(i.hash == DEPLOY_TRANSACTION_HASH for i in block.transactions)


@pytest.mark.asyncio
async def test_get_storage_at():
    client = DevnetClientWithoutAccount()
    storage = await client.get_storage_at(
        contract_address=CONTRACT_ADDRESS,
        key=916907772491729262376534102982219947830828984996257231353398618781993312401,
    )

    assert storage == 1234


@pytest.mark.asyncio
async def test_get_storage_at_incorrect_address():
    client = DevnetClientWithoutAccount()
    storage = await client.get_storage_at(
        contract_address=0x1111,
        key=916907772491729262376534102982219947830828984996257231353398618781993312401,
    )

    assert storage == 0


@pytest.mark.asyncio
async def test_get_transaction_receipt():
    client = DevnetClientWithoutAccount()
    receipt = await client.get_transaction_receipt(tx_hash=INVOKE_TRANSACTION_HASH)

    assert receipt.hash == INVOKE_TRANSACTION_HASH
    assert receipt.status in (
        TransactionStatus.ACCEPTED_ON_L1,
        TransactionStatus.ACCEPTED_ON_L2,
    )


@pytest.mark.asyncio
async def test_get_code():
    client = DevnetClientWithoutAccount()
    code = await client.get_code(contract_address=CONTRACT_ADDRESS)

    assert code.abi is not None
    assert len(code.abi) != 0
    assert code.bytecode is not None
    assert len(code.bytecode) != 0


@pytest.mark.asyncio
async def test_estimate_fee():
    client = DevnetClientWithoutAccount()
    transaction = InvokeFunction(
        contract_address=CONTRACT_ADDRESS,
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
async def test_call_contract():
    client = DevnetClientWithoutAccount()
    invoke_function = InvokeFunction(
        contract_address=CONTRACT_ADDRESS,
        entry_point_selector=get_selector_from_name("get_balance"),
        calldata=[],
        max_fee=0,
        version=0,
        signature=[0x0, 0x0],
    )
    result = await client.call_contract(invoke_function)

    assert result == [1234]


@pytest.mark.asyncio
async def test_add_transaction():
    client = DevnetClientWithoutAccount()
    invoke_function = InvokeFunction(
        contract_address=CONTRACT_ADDRESS,
        entry_point_selector=get_selector_from_name("increase_balance"),
        calldata=[0],
        max_fee=0,
        version=0,
        signature=[0x0, 0x0],
    )
    result = await client.add_transaction(invoke_function)

    assert result.address == CONTRACT_ADDRESS
    assert result.code == "TRANSACTION_RECEIVED"


@pytest.mark.asyncio
async def test_deploy():
    client = DevnetClientWithoutAccount()
    result = await client.deploy(contract=BALANCE_CONTRACT, constructor_calldata=[])

    assert result.code == "TRANSACTION_RECEIVED"
