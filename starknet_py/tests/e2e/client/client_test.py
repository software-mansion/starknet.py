# pylint: disable=too-many-arguments
import pytest

from starkware.starknet.public.abi import get_selector_from_name

from starknet_py.tests.e2e.utils import DevnetClientFactory
from starknet_py.net.client_models import (
    TransactionType,
    TransactionStatus,
    InvokeFunction,
    BlockStateUpdate,
    Transaction,
    StarknetBlock,
    BlockStatus,
    TransactionReceipt,
    ContractDiff,
)
from starknet_py.net.client_errors import ClientError
from starknet_py.transactions.deploy import make_deploy_tx


@pytest.mark.asyncio
async def test_get_deploy_transaction(
    clients, deploy_transaction_hash, contract_address
):
    for client in clients:
        transaction = await client.get_transaction(deploy_transaction_hash)

        assert transaction == Transaction(
            contract_address=contract_address,
            calldata=[],
            entry_point_selector=0x0,
            hash=deploy_transaction_hash,
            signature=[],
            transaction_type=TransactionType.DEPLOY,
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

        assert transaction == Transaction(
            contract_address=contract_address,
            calldata=invoke_transaction_calldata,
            entry_point_selector=invoke_transaction_selector,
            hash=invoke_transaction_hash,
            signature=[],
            transaction_type=TransactionType.INVOKE,
        )


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
            parent_block_hash=0x0,
            root=block_with_deploy_root,
            status=BlockStatus.ACCEPTED_ON_L2,
            timestamp=2137,
            transactions=[
                Transaction(
                    contract_address=contract_address,
                    calldata=[],
                    entry_point_selector=0x0,
                    hash=deploy_transaction_hash,
                    signature=[],
                    transaction_type=TransactionType.DEPLOY,
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
            parent_block_hash=0x0,
            root=block_with_deploy_root,
            status=BlockStatus.ACCEPTED_ON_L2,
            timestamp=2137,
            transactions=[
                Transaction(
                    contract_address=contract_address,
                    calldata=[],
                    entry_point_selector=0x0,
                    hash=deploy_transaction_hash,
                    signature=[],
                    transaction_type=TransactionType.DEPLOY,
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

    with pytest.raises(ClientError):
        await full_node_client.get_storage_at(
            contract_address=0x1111,
            key=916907772491729262376534102982219947830828984996257231353398618781993312401,
            block_hash="latest",
        )


@pytest.mark.asyncio
async def test_get_transaction_receipt(clients, invoke_transaction_hash):
    for client in clients:
        receipt = await client.get_transaction_receipt(tx_hash=invoke_transaction_hash)

        assert receipt == TransactionReceipt(
            hash=invoke_transaction_hash,
            status=TransactionStatus.ACCEPTED_ON_L2,
            events=[],
            l2_to_l1_messages=[],
            l1_to_l2_consumed_message=None,
            version=0,
            actual_fee=0,
            transaction_rejection_reason=None,
        )


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

    assert isinstance(estimate_fee, int)
    assert estimate_fee > 0


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
async def test_state_update(
    clients, block_with_deploy_hash, block_with_deploy_root, contract_address
):
    for client in clients:
        state_update = await client.get_state_update(block_hash=block_with_deploy_hash)

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
        )


@pytest.mark.asyncio
async def test_add_transaction(devnet_address, contract_address):
    # TODO extend this test to all clients
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
    # TODO extend this test to all clients
    client = await DevnetClientFactory(
        devnet_address
    ).make_devnet_client_without_account()
    deploy_tx = make_deploy_tx(
        compiled_contract=balance_contract, constructor_calldata=[]
    )
    result = await client.deploy(deploy_tx)

    assert result.code == "TRANSACTION_RECEIVED"


@pytest.mark.asyncio
async def test_get_class_hash_at(devnet_address, contract_address):
    # TODO extend this test to all clients
    client = await DevnetClientFactory(
        devnet_address
    ).make_devnet_client_without_account()
    class_hash = await client.get_class_hash_at(contract_address=contract_address)
    assert (
        class_hash == 0x711941B11A8236B8CCA42B664E19342AC7300ABB1DC44957763CB65877C2708
    )


@pytest.mark.asyncio
async def test_get_class_by_hash(devnet_address, class_hash):
    # TODO extend this test to all clients
    client = await DevnetClientFactory(
        devnet_address
    ).make_devnet_client_without_account()
    contract_class = await client.get_class_by_hash(class_hash=class_hash)
    assert contract_class.program != ""
    assert contract_class.entry_points_by_type is not None
