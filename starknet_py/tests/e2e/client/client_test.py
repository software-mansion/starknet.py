# pylint: disable=too-many-arguments
import asyncio
from unittest.mock import patch, MagicMock

import pytest
from aiohttp import ClientSession

from starkware.starknet.public.abi import (
    get_selector_from_name,
    get_storage_var_address,
)

from starknet_py.net.client_models import (
    TransactionStatus,
    InvokeFunction,
    TransactionReceipt,
    DeployTransaction,
    Call,
    GatewayBlock,
)
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.tests.e2e.account.account_client_test import MAX_FEE
from starknet_py.transaction_exceptions import (
    TransactionRejectedError,
    TransactionNotReceivedError,
)
from starknet_py.transactions.declare import make_declare_tx
from starknet_py.transactions.deploy import make_deploy_tx


@pytest.mark.asyncio
async def test_get_deploy_transaction(
    client, deploy_transaction_hash, contract_address, class_hash
):
    transaction = await client.get_transaction(deploy_transaction_hash)

    assert transaction == DeployTransaction(
        contract_address=contract_address,
        constructor_calldata=[],
        hash=deploy_transaction_hash,
        signature=[],
        max_fee=0,
        class_hash=class_hash,
        version=0,
    )


@pytest.mark.asyncio
async def test_get_declare_transaction(
    client,
    declare_transaction_hash,
    class_hash,
    sender_address,
):
    transaction = await client.get_transaction(declare_transaction_hash)

    assert transaction.class_hash == class_hash
    assert transaction.hash == declare_transaction_hash
    assert transaction.sender_address == sender_address[transaction.version]


@pytest.mark.asyncio
async def test_get_invoke_transaction(
    client,
    invoke_transaction_hash,
):
    transaction = await client.get_transaction(invoke_transaction_hash)

    assert any(data == 1234 for data in transaction.calldata)
    assert transaction.hash == invoke_transaction_hash


@pytest.mark.asyncio
async def test_get_transaction_raises_on_not_received(client):
    with pytest.raises(TransactionNotReceivedError) as err:
        await client.get_transaction(tx_hash=0x1)

    assert str(err.value) == "Transaction was not received on starknet"
    assert err.value.message == "Transaction not received"


@pytest.mark.asyncio
async def test_get_block_by_hash(
    client,
    deploy_transaction_hash,
    block_with_deploy_hash,
    block_with_deploy_number,
    contract_address,
    class_hash,
):
    block = await client.get_block(block_hash=block_with_deploy_hash)

    assert block.block_number == block_with_deploy_number
    assert block.block_hash == block_with_deploy_hash
    assert (
        DeployTransaction(
            contract_address=contract_address,
            constructor_calldata=[],
            hash=deploy_transaction_hash,
            signature=[],
            max_fee=0,
            class_hash=class_hash,
            version=0,
        )
        in block.transactions
    )

    if isinstance(client, GatewayClient):
        assert block.gas_price > 0


@pytest.mark.asyncio
async def test_get_block_by_number(
    client,
    deploy_transaction_hash,
    block_with_deploy_number,
    block_with_deploy_hash,
    contract_address,
    class_hash,
):
    block = await client.get_block(block_number=block_with_deploy_number)

    assert block.block_number == block_with_deploy_number
    assert block.block_hash == block_with_deploy_hash
    assert (
        DeployTransaction(
            contract_address=contract_address,
            constructor_calldata=[],
            hash=deploy_transaction_hash,
            signature=[],
            class_hash=class_hash,
            max_fee=0,
            version=0,
        )
        in block.transactions
    )

    if isinstance(client, GatewayClient):
        assert block.gas_price == default_gateway_gas_price


@pytest.mark.asyncio
async def test_get_storage_at(client, contract_address):
    storage = await client.get_storage_at(
        contract_address=contract_address,
        key=get_storage_var_address("balance"),
        block_hash="latest",
    )

    assert storage == 1234


@pytest.mark.asyncio
async def test_get_transaction_receipt(
    client, invoke_transaction_hash, block_with_invoke_number
):
    receipt = await client.get_transaction_receipt(tx_hash=invoke_transaction_hash)

    assert receipt.hash == invoke_transaction_hash
    assert receipt.block_number == block_with_invoke_number


@pytest.mark.asyncio
async def test_estimate_fee(contract_address, client):
    transaction = InvokeFunction(
        contract_address=contract_address,
        entry_point_selector=get_selector_from_name("increase_balance"),
        calldata=[123],
        max_fee=0,
        version=0,
        signature=[0x0, 0x0],
        nonce=None,
    )

    estimate_fee = await client.estimate_fee(tx=transaction, block_number="latest")

    assert isinstance(estimate_fee.overall_fee, int)
    assert estimate_fee.overall_fee > 0


@pytest.mark.asyncio
async def test_call_contract(client, contract_address):
    call = Call(
        to_addr=contract_address,
        selector=get_selector_from_name("get_balance"),
        calldata=[],
    )

    result = await client.call_contract(call, block_hash="latest")

    assert result == [1234]


@pytest.mark.asyncio
async def test_add_transaction(map_contract, client, gateway_account_client):
    prepared_function_call = map_contract.functions["put"].prepare(key=73, value=12)
    signed_invoke = await gateway_account_client.sign_invoke_transaction(
        calls=prepared_function_call, max_fee=MAX_FEE
    )

    result = await client.send_transaction(signed_invoke)
    await client.wait_for_tx(result.transaction_hash)
    transaction_receipt = await client.get_transaction_receipt(result.transaction_hash)

    assert transaction_receipt.status != TransactionStatus.NOT_RECEIVED


@pytest.mark.asyncio
async def test_deploy(balance_contract, client):
    deploy_tx = make_deploy_tx(
        compiled_contract=balance_contract, constructor_calldata=[]
    )
    result = await client.deploy(deploy_tx)
    await client.wait_for_tx(result.transaction_hash)
    transaction_receipt = await client.get_transaction_receipt(result.transaction_hash)

    assert transaction_receipt.status != TransactionStatus.NOT_RECEIVED
    assert transaction_receipt.hash
    assert transaction_receipt.actual_fee == 0


@pytest.mark.asyncio
async def test_get_class_hash_at(client, contract_address, class_hash):
    received_class_hash = await client.get_class_hash_at(
        contract_address=contract_address, block_hash="latest"
    )
    assert received_class_hash == class_hash


@pytest.mark.asyncio
async def test_get_class_by_hash(client, class_hash):
    contract_class = await client.get_class_by_hash(class_hash=class_hash)
    assert contract_class.program != ""
    assert contract_class.entry_points_by_type is not None


@pytest.mark.asyncio
async def test_wait_for_tx_accepted(gateway_client):
    with patch(
        "starknet_py.net.gateway_client.GatewayClient.get_transaction_receipt",
        MagicMock(),
    ) as mocked_receipt:
        result = asyncio.Future()
        result.set_result(
            TransactionReceipt(
                hash=0x1, status=TransactionStatus.ACCEPTED_ON_L2, block_number=1
            )
        )

        mocked_receipt.return_value = result

        block_number, tx_status = await gateway_client.wait_for_tx(tx_hash=0x1)
        assert block_number == 1
        assert tx_status == TransactionStatus.ACCEPTED_ON_L2


@pytest.mark.asyncio
async def test_wait_for_tx_pending(gateway_client):
    with patch(
        "starknet_py.net.gateway_client.GatewayClient.get_transaction_receipt",
        MagicMock(),
    ) as mocked_receipt:
        result = asyncio.Future()
        result.set_result(
            TransactionReceipt(
                hash=0x1, status=TransactionStatus.PENDING, block_number=1
            )
        )

        mocked_receipt.return_value = result

        block_number, tx_status = await gateway_client.wait_for_tx(tx_hash=0x1)
        assert block_number == 1
        assert tx_status == TransactionStatus.PENDING


@pytest.mark.parametrize(
    "status, exception, exc_message",
    (
        (
            TransactionStatus.REJECTED,
            TransactionRejectedError,
            "Unknown starknet error",
        ),
        (
            TransactionStatus.NOT_RECEIVED,
            TransactionNotReceivedError,
            "Transaction not received",
        ),
    ),
)
@pytest.mark.asyncio
async def test_wait_for_tx_rejected(status, exception, exc_message, gateway_client):
    with patch(
        "starknet_py.net.gateway_client.GatewayClient.get_transaction_receipt",
        MagicMock(),
    ) as mocked_receipt:
        result = asyncio.Future()
        result.set_result(
            TransactionReceipt(
                hash=0x1, status=status, block_number=1, rejection_reason=exc_message
            )
        )

        mocked_receipt.return_value = result

        with pytest.raises(exception) as err:
            await gateway_client.wait_for_tx(tx_hash=0x1)

        assert exc_message in err.value.message


@pytest.mark.asyncio
async def test_wait_for_tx_cancelled(gateway_client):
    with patch(
        "starknet_py.net.gateway_client.GatewayClient.get_transaction_receipt",
        MagicMock(),
    ) as mocked_receipt:
        result = asyncio.Future()
        result.set_result(
            TransactionReceipt(
                hash=0x1, status=TransactionStatus.PENDING, block_number=1
            )
        )

        mocked_receipt.return_value = result

        task = asyncio.create_task(
            gateway_client.wait_for_tx(tx_hash=0x1, wait_for_accept=True)
        )
        await asyncio.sleep(1)
        task.cancel()

        with pytest.raises(TransactionNotReceivedError):
            await task


@pytest.mark.asyncio
async def test_declare_contract(client, map_source_code):
    declare_tx = make_declare_tx(compilation_source=map_source_code)

    result = await client.declare(declare_tx)
    await client.wait_for_tx(result.transaction_hash)
    transaction_receipt = await client.get_transaction_receipt(result.transaction_hash)

    assert transaction_receipt.status != TransactionStatus.NOT_RECEIVED
    assert transaction_receipt.hash
    assert transaction_receipt.actual_fee == 0


@pytest.mark.asyncio
async def test_custom_session(map_contract, network):
    # We must access protected `feeder_gateway_client` to test session
    # pylint: disable=protected-access

    session = ClientSession()

    tx_hash = (
        await (
            await map_contract.functions["put"].invoke(
                key=10, value=20, max_fee=MAX_FEE
            )
        ).wait_for_acceptance()
    ).hash

    gateway_client1 = GatewayClient(net=network, session=session)
    gateway_client2 = GatewayClient(net=network, session=session)

    assert gateway_client1._feeder_gateway_client.session is not None
    assert gateway_client1._feeder_gateway_client.session == session
    assert gateway_client1._feeder_gateway_client.session.closed is False
    assert gateway_client2._feeder_gateway_client.session is not None
    assert gateway_client2._feeder_gateway_client.session == session
    assert gateway_client2._feeder_gateway_client.session.closed is False

    gateway1_response = await gateway_client1.get_transaction_receipt(tx_hash=tx_hash)
    gateway2_response = await gateway_client2.get_transaction_receipt(tx_hash=tx_hash)
    assert gateway1_response == gateway2_response

    assert gateway_client1._feeder_gateway_client.session.closed is False
    assert gateway_client2._feeder_gateway_client.session.closed is False

    await session.close()

    assert gateway_client1._feeder_gateway_client.session.closed is True
    assert gateway_client2._feeder_gateway_client.session.closed is True
