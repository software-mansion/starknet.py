# pylint: disable=too-many-arguments
import asyncio
from unittest.mock import patch, MagicMock

import pytest

from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.gateway.transaction import DECLARE_SENDER_ADDRESS

from starknet_py.net.models import StarknetChainId
from starknet_py.net.client_models import (
    TransactionStatus,
    InvokeFunction,
    BlockStateUpdate,
    StarknetBlock,
    BlockStatus,
    TransactionReceipt,
    ContractDiff,
    DeployTransaction,
    DeclareTransaction,
    InvokeTransaction,
)
from starknet_py.net.client_errors import ClientError
from starknet_py.transaction_exceptions import (
    TransactionRejectedError,
    TransactionNotReceivedError,
)
from starknet_py.transactions.declare import make_declare_tx
from starknet_py.transactions.deploy import make_deploy_tx


@pytest.mark.asyncio
async def test_get_deploy_transaction(
    clients, deploy_transaction_hash, contract_address
):
    for client in clients:
        transaction = await client.get_transaction(deploy_transaction_hash)

        assert transaction == DeployTransaction(
            contract_address=contract_address,
            constructor_calldata=[],
            hash=deploy_transaction_hash,
            signature=[],
            max_fee=0,
            # class_hash=class_hash,
        )


@pytest.mark.asyncio
async def test_get_declare_transaction(clients, declare_transaction_hash, class_hash):
    # TODO extend this test to all clients
    gateway_client, _ = clients

    transaction = await gateway_client.get_transaction(declare_transaction_hash)

    assert transaction == DeclareTransaction(
        class_hash=class_hash,
        sender_address=DECLARE_SENDER_ADDRESS,
        hash=declare_transaction_hash,
        signature=[],
        max_fee=0,
    )


@pytest.mark.asyncio
async def test_get_invoke_transaction(
    clients,
    invoke_transaction_hash,
    invoke_transaction_calldata,
    invoke_transaction_selector,
    contract_address,
):
    for client in clients:
        transaction = await client.get_transaction(invoke_transaction_hash)

        assert transaction == InvokeTransaction(
            contract_address=contract_address,
            calldata=invoke_transaction_calldata,
            entry_point_selector=invoke_transaction_selector,
            hash=invoke_transaction_hash,
            signature=[],
            max_fee=0,
        )


@pytest.mark.asyncio
async def test_get_transaction_raises_on_not_received(clients):
    for client in clients:
        with pytest.raises(TransactionNotReceivedError) as err:
            await client.get_transaction(tx_hash=0x1)

        assert str(err.value) == "Transaction was not received on starknet"
        assert err.value.message == "Transaction not received"


@pytest.mark.asyncio
async def test_get_block_by_hash(
    clients,
    deploy_transaction_hash,
    block_with_deploy_hash,
    block_with_deploy_number,
    block_with_deploy_root,
    contract_address,
):
    for client in clients:
        block = await client.get_block(block_hash=block_with_deploy_hash)

        assert block == StarknetBlock(
            block_number=block_with_deploy_number,
            block_hash=block_with_deploy_hash,
            gas_price=100_000_000_000,
            parent_block_hash=0x0,
            root=block_with_deploy_root,
            status=BlockStatus.ACCEPTED_ON_L2,
            timestamp=2137,
            transactions=[
                DeployTransaction(
                    contract_address=contract_address,
                    constructor_calldata=[],
                    hash=deploy_transaction_hash,
                    signature=[],
                    max_fee=0,
                    # class_hash=class_hash,
                )
            ],
        )


@pytest.mark.asyncio
async def test_get_block_by_number(
    clients,
    deploy_transaction_hash,
    block_with_deploy_number,
    block_with_deploy_hash,
    block_with_deploy_root,
    contract_address,
):
    for client in clients:
        block = await client.get_block(block_number=0)

        assert block == StarknetBlock(
            block_number=block_with_deploy_number,
            block_hash=block_with_deploy_hash,
            gas_price=100_000_000_000,
            parent_block_hash=0x0,
            root=block_with_deploy_root,
            status=BlockStatus.ACCEPTED_ON_L2,
            timestamp=2137,
            transactions=[
                DeployTransaction(
                    contract_address=contract_address,
                    constructor_calldata=[],
                    hash=deploy_transaction_hash,
                    signature=[],
                    # class_hash=class_hash,
                    max_fee=0,
                )
            ],
        )


@pytest.mark.asyncio
async def test_get_storage_at(clients, contract_address):
    for client in clients:
        storage = await client.get_storage_at(
            contract_address=contract_address,
            key=916907772491729262376534102982219947830828984996257231353398618781993312401,
            block_hash="latest",
        )

        assert storage == 1234


@pytest.mark.asyncio
async def test_get_storage_at_incorrect_address(clients):
    gateway_client, full_node_client = clients

    storage = await gateway_client.get_storage_at(
        contract_address=0x1111,
        key=916907772491729262376534102982219947830828984996257231353398618781993312401,
        block_hash="latest",
    )
    assert storage == 0

    with pytest.raises(ClientError) as err:
        await full_node_client.get_storage_at(
            contract_address=0x1111,
            key=916907772491729262376534102982219947830828984996257231353398618781993312401,
            block_hash="latest",
        )
    assert "Contract not found" in err.value.message


@pytest.mark.asyncio
async def test_get_transaction_receipt(clients, invoke_transaction_hash):
    # TODO: Adapt this test to work with RPC as well when it returns block number
    gateway_client, _ = clients
    receipt = await gateway_client.get_transaction_receipt(
        tx_hash=invoke_transaction_hash
    )

    assert receipt == TransactionReceipt(
        hash=invoke_transaction_hash,
        status=TransactionStatus.ACCEPTED_ON_L2,
        events=[],
        l2_to_l1_messages=[],
        l1_to_l2_consumed_message=None,
        version=0,
        actual_fee=0,
        rejection_reason=None,
        block_number=1,
    )


@pytest.mark.asyncio
async def test_estimate_fee(contract_address, gateway_client):
    transaction = InvokeFunction(
        contract_address=contract_address,
        entry_point_selector=get_selector_from_name("increase_balance"),
        calldata=[123],
        max_fee=0,
        version=0,
        signature=[0x0, 0x0],
    )
    estimate_fee = await gateway_client.estimate_fee(tx=transaction)

    assert isinstance(estimate_fee.overall_fee, int)
    assert estimate_fee.overall_fee > 0


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
async def test_state_update_gateway_client(
    gateway_client, block_with_deploy_hash, block_with_deploy_root, contract_address
):
    state_update = await gateway_client.get_state_update(
        block_hash=block_with_deploy_hash
    )

    assert state_update == BlockStateUpdate(
        block_hash=block_with_deploy_hash,
        new_root=block_with_deploy_root,
        old_root=0x0,
        storage_diffs=[],
        contract_diffs=[
            ContractDiff(
                address=contract_address,
                contract_hash=0x711941B11A8236B8CCA42B664E19342AC7300ABB1DC44957763CB65877C2708,
            )
        ],
        declared_contracts=[
            0x711941B11A8236B8CCA42B664E19342AC7300ABB1DC44957763CB65877C2708
        ],
    )


@pytest.mark.asyncio
async def test_state_update_full_node_client(
    rpc_client, block_with_deploy_hash, block_with_deploy_root, contract_address
):
    state_update = await rpc_client.get_state_update(block_hash=block_with_deploy_hash)

    assert state_update == BlockStateUpdate(
        block_hash=block_with_deploy_hash,
        new_root=block_with_deploy_root,
        old_root=0x0,
        storage_diffs=[],
        contract_diffs=[
            ContractDiff(
                address=contract_address,
                contract_hash=0x711941B11A8236B8CCA42B664E19342AC7300ABB1DC44957763CB65877C2708,
            )
        ],
        declared_contracts=[],
    )


@pytest.mark.asyncio
async def test_add_transaction(contract_address, clients):
    for client in clients:
        invoke_function = InvokeFunction(
            contract_address=contract_address,
            entry_point_selector=get_selector_from_name("increase_balance"),
            calldata=[0],
            max_fee=0,
            version=0,
            signature=[0x0, 0x0],
        )
        result = await client.send_transaction(invoke_function)
        transaction_receipt = await client.get_transaction_receipt(
            result.transaction_hash
        )

        assert transaction_receipt.status != TransactionStatus.NOT_RECEIVED


@pytest.mark.asyncio
async def test_deploy(balance_contract, clients):
    for client in clients:
        deploy_tx = make_deploy_tx(
            compiled_contract=balance_contract, constructor_calldata=[]
        )
        result = await client.deploy(deploy_tx)
        transaction_receipt = await client.get_transaction_receipt(
            result.transaction_hash
        )

        assert transaction_receipt.status != TransactionStatus.NOT_RECEIVED
        assert transaction_receipt.hash
        assert transaction_receipt.actual_fee == 0


async def test_get_class_hash_at(clients, contract_address):
    for client in clients:
        class_hash = await client.get_class_hash_at(contract_address=contract_address)
        assert (
            class_hash
            == 0x711941B11A8236B8CCA42B664E19342AC7300ABB1DC44957763CB65877C2708
        )


@pytest.mark.asyncio
async def test_get_class_by_hash(clients, class_hash):
    for client in clients:
        contract_class = await client.get_class_by_hash(class_hash=class_hash)
        assert contract_class.program != ""
        assert contract_class.entry_points_by_type is not None


def test_chain_id(clients):
    for client in clients:
        assert client.chain == StarknetChainId.TESTNET


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
async def test_declare_contract(clients, map_source_code):
    for client in clients:
        declare_tx = make_declare_tx(compilation_source=map_source_code)

        result = await client.declare(declare_tx)
        transaction_receipt = await client.get_transaction_receipt(
            result.transaction_hash
        )

        assert transaction_receipt.status != TransactionStatus.NOT_RECEIVED
        assert transaction_receipt.hash
        assert transaction_receipt.actual_fee == 0
