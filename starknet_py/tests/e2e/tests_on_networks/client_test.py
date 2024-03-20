import dataclasses
import sys

import pytest

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    BlockHeader,
    BlockStatus,
    Call,
    DAMode,
    DeclareTransactionV3,
    DeployAccountTransactionV3,
    EmittedEvent,
    EstimatedFee,
    EventsChunk,
    InvokeTransactionV3,
    PendingBlockHeader,
    PendingStarknetBlockWithReceipts,
    ResourceBoundsMapping,
    StarknetBlockWithReceipts,
    TransactionExecutionStatus,
    TransactionFinalityStatus,
    TransactionReceipt,
    TransactionStatus,
)
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import SEPOLIA_TESTNET, default_token_address_for_network
from starknet_py.tests.e2e.fixtures.constants import (
    EMPTY_CONTRACT_ADDRESS_SEPOLIA_TESTNET,
)
from starknet_py.transaction_errors import TransactionRevertedError


@pytest.mark.parametrize(
    "transaction_hash",
    (
        "0x016df225d14eb927b1c85ec85d2f9f4fc7653ba13a99e30ffe9e21c96ddc7a6d",  # invoke
        "0x0255f63b1dbd52902e2fb5707d2d2b52d5600fa228f0655b02b78bfcf9cab353",  # declare
        # "0x510fa73cdb49ae81742441c494c396883a2eee91209fe387ce1dec5fa04ecb",  # deploy
        "0x0379c52f40fad2d94152d7c924b69cd61a99cf45b85ba9cb836f69026db67af8",  # deploy_account
        "0x06098d74f3fe1b2b96dcfbb3b9ca9be0c396bde0a0825e111fcbefec9c34fcc6",  # l1_handler
    ),
)
@pytest.mark.asyncio
async def test_get_transaction_receipt(client_sepolia_testnet, transaction_hash):
    receipt = await client_sepolia_testnet.get_transaction_receipt(
        tx_hash=transaction_hash
    )

    assert isinstance(receipt, TransactionReceipt)
    assert receipt.execution_status is not None
    assert receipt.finality_status is not None
    assert receipt.execution_resources is not None
    assert receipt.type is not None


@pytest.mark.asyncio
async def test_wait_for_tx_reverted(account_sepolia_testnet):
    account = account_sepolia_testnet
    # Calldata too long for the function (it has no parameters) to trigger REVERTED status
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[0x1, 0x2, 0x3, 0x4, 0x5],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=int(1e16))
    invoke = await account.client.send_transaction(sign_invoke)

    with pytest.raises(TransactionRevertedError, match="Input too long for arguments"):
        await account.client.wait_for_tx(tx_hash=invoke.transaction_hash)


@pytest.mark.asyncio
async def test_wait_for_tx_accepted(account_sepolia_testnet):
    account = account_sepolia_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=int(1e16))
    invoke = await account.client.send_transaction(sign_invoke)

    result = await account.client.wait_for_tx(tx_hash=invoke.transaction_hash)

    assert result.execution_status == TransactionExecutionStatus.SUCCEEDED
    assert result.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2


@pytest.mark.asyncio
async def test_transaction_not_received_max_fee_too_small(account_sepolia_testnet):
    account = account_sepolia_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=int(1e10))

    with pytest.raises(ClientError, match=r".*MaxFeeTooLow.*"):
        await account.client.send_transaction(sign_invoke)


@pytest.mark.asyncio
async def test_transaction_not_received_max_fee_too_big(account_sepolia_testnet):
    account = account_sepolia_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=sys.maxsize)

    with pytest.raises(ClientError, match=r".*max_fee.*"):
        await account.client.send_transaction(sign_invoke)


@pytest.mark.asyncio
async def test_transaction_not_received_invalid_nonce(account_sepolia_testnet):
    account = account_sepolia_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=int(1e16), nonce=0)

    with pytest.raises(ClientError, match=r".*nonce.*"):
        await account.client.send_transaction(sign_invoke)


@pytest.mark.asyncio
async def test_transaction_not_received_invalid_signature(account_sepolia_testnet):
    account = account_sepolia_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=int(1e16))
    sign_invoke = dataclasses.replace(sign_invoke, signature=[0x21, 0x37])
    # 0x0000000000004163636f756e743a20696e76616c6964207369676e6174757265 -> Account: invalid signature
    with pytest.raises(
        ClientError,
        match=r"0x0000000000004163636f756e743a20696e76616c6964207369676e6174757265",
    ) as exc:
        await account.client.send_transaction(sign_invoke)

    assert exc.value.data is not None
    assert "Data:" in exc.value.message


# TODO (#1219): move tests below to full_node_test.py


@pytest.mark.skip(reason="Check why it doesen't works")
@pytest.mark.asyncio
async def test_estimate_message_fee(client_sepolia_testnet):
    client = client_sepolia_testnet

    # info about this message from
    # https://sepolia.starkscan.co/tx/0x073b6ed980a1ee0aba8499ff41cd4fa6432ae1348876b675697485cc4dbe586b#overview
    # https://integration.starkscan.co/message/0x140185c79e5a04c7c3fae513001f358beb66653dcee75be38f05bd30adba85dd
    estimated_message = await client.estimate_message_fee(
        from_address="0x2ffb3c4bbe0fc6e7a6f90ebfd50099dfbaa80ab9",
        block_number=41044,
        to_address="0x07fd01e7edd2a555ff389efb8335b75c3e3372f8f77aab4902a0bdb28e885975",
        entry_point_selector="0x03636c566f6409560d55d5f6d1eb4ee163b096b4698c503e69e210be79de2afa",
        payload=[
            "0xe",
            "0x0",
            "0xa7d66ab47e22255e4c72e5f07a511f31b53beb68",
            "0x2386f26fc10000",
            "0x0",
        ],
    )

    assert isinstance(estimated_message, EstimatedFee)
    assert estimated_message.overall_fee > 0
    assert estimated_message.gas_price > 0
    assert estimated_message.gas_consumed > 0
    assert estimated_message.data_gas_price > 0
    assert estimated_message.data_gas_consumed >= 0
    assert estimated_message.unit is not None


@pytest.mark.asyncio
async def test_estimate_message_fee_invalid_eth_address_assertion_error(
    client_sepolia_testnet,
):
    client = client_sepolia_testnet
    invalid_eth_address = "0xD"

    # info about this transaction from
    # https://sepolia.starkscan.co/tx/0x07041ce61b01f677ef05391ae1db043d0ea8b96309574ddcf90e7f59ec7d76d6
    with pytest.raises(
        AssertionError,
        match=f"Argument 'from_address': {invalid_eth_address} is not a valid Ethereum address.",
    ):
        _ = await client.estimate_message_fee(
            from_address=invalid_eth_address,
            block_number=41044,
            to_address="0x07fd01e7edd2a555ff389efb8335b75c3e3372f8f77aab4902a0bdb28e885975",
            entry_point_selector="0x03636c566f6409560d55d5f6d1eb4ee163b096b4698c503e69e210be79de2afa",
            payload=[
                "0xe",
                "0x0",
                "0xa7d66ab47e22255e4c72e5f07a511f31b53beb68",
                "0x2386f26fc10000",
                "0x0",
            ],
        )


@pytest.mark.parametrize(
    "from_address, to_address",
    (
        (
            "0xbe1259ff905cadbbaa62514388b71bdefb8aacc1",
            "0x2137",
        ),  # valid `from_address`, invalid `to_address`
        (
            "0xDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",
            "0x073314940630fd6dcda0d772d4c972c4e0a9946bef9dabf4ef84eda8ef542b82",
        ),  # invalid `from_address` (passes through assert), valid `to_address`
    ),
)
@pytest.mark.asyncio
async def test_estimate_message_fee_throws(
    client_sepolia_integration, from_address, to_address
):
    client = client_sepolia_integration

    with pytest.raises(ClientError):
        _ = await client.estimate_message_fee(
            block_number=123123,
            from_address=from_address,
            to_address=to_address,
            entry_point_selector="0x3248",
            payload=[
                "0x4359",
            ],
        )


@pytest.mark.asyncio
async def test_get_tx_receipt_reverted(client_sepolia_integration):
    client = client_sepolia_integration
    reverted_tx_hash = (
        "0x01b2d9e5a725069ae40e3149813ffe05b8c4405e253e9f8ab29d0a3b2e279927"
    )

    res = await client.get_transaction_receipt(tx_hash=reverted_tx_hash)

    assert res.execution_status == TransactionExecutionStatus.REVERTED
    assert res.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L1
    assert "Got an exception while executing a hint" in res.revert_reason


@pytest.mark.parametrize(
    "block_number, transaction_index",
    [
        # declare: https://integration-sepolia.starkscan.co/tx/0x0544a629990d2bed8ccf11910b30f2f1e18228ed5be06660bea20cae13b2aced
        (9707, 0),
        # Deploys on sepolia integration are marks as inveke
        # deploy: https://integration.voyager.online/tx/0x510fa73cdb49ae81742441c494c396883a2eee91209fe387ce1dec5fa04ecb
        # (248061, 0),
        # deploy_account: https://integration.voyager.online/tx/0x593c073960140ab7af7951fadb6a129572cc504ef0b9107992c5c1efe5a0fb5
        (9708, 6),
        # invoke: https://integration-sepolia.starkscan.co/tx/0x069125fd85a199a5d06445e1ece5067781aa46c745e3e2993c696c60bbd5992c
        (9708, 0),
        # l1_handler: https://integration-sepolia.starkscan.co/tx/0x0117be3e303704f0acb630149250a78a262ecff8bef3ee8a53a02f18b472f873
        (9708, 7),
    ],
)
@pytest.mark.asyncio
async def test_get_transaction_by_block_id_and_index(
    client_sepolia_integration, block_number, transaction_index
):
    client = client_sepolia_integration

    tx = await client.get_transaction_by_block_id(
        block_number=block_number, index=transaction_index
    )

    assert tx.hash is not None

    receipt = await client.get_transaction_receipt(tx_hash=tx.hash)

    assert receipt.finality_status is not None
    assert receipt.execution_status is not None


@pytest.mark.asyncio
async def test_get_block(client_goerli_integration):
    client = client_goerli_integration
    res = await client.get_block(block_number="latest")

    for tx in res.transactions:
        assert tx.hash is not None


@pytest.mark.asyncio
async def test_get_l1_message_hash(client_goerli_integration):
    tx_hash = "0x0060bd50c38082211e6aedb21838fe7402a67216d559d9a4848e6c5e9670c90e"
    l1_message_hash = await client_goerli_integration.get_l1_message_hash(tx_hash)
    assert (
        hex(l1_message_hash)
        == "0x140185c79e5a04c7c3fae513001f358beb66653dcee75be38f05bd30adba85dd"
    )


@pytest.mark.asyncio
async def test_get_l1_message_hash_raises_on_incorrect_transaction_type(
    client_goerli_integration,
):
    tx_hash = "0x06d11fa74255c1f86aace54cbf382ab8c89e2b90fb0801f751834ca52bf2a2a2"
    with pytest.raises(
        TypeError, match=f"Transaction {tx_hash} is not a result of L1->L2 interaction."
    ):
        await client_goerli_integration.get_l1_message_hash(tx_hash)


@pytest.mark.asyncio
async def test_spec_version(client_goerli_testnet):
    spec_version = await client_goerli_testnet.spec_version()

    assert spec_version is not None
    assert isinstance(spec_version, str)


@pytest.mark.asyncio
async def test_get_transaction_status(client_goerli_testnet):
    tx_status = await client_goerli_testnet.get_transaction_status(
        tx_hash=0x1FCE504A8F9C837CA84B784836E5AF041221C1BFB40C03AE0BDC0C713D09A21
    )

    assert tx_status.finality_status == TransactionStatus.ACCEPTED_ON_L1
    assert tx_status.execution_status == TransactionExecutionStatus.SUCCEEDED


@pytest.mark.asyncio
async def test_get_block_new_header_fields(client_goerli_testnet):
    # testing l1_gas_price and starknet_version fields
    block = await client_goerli_testnet.get_block_with_txs(block_number=800000)

    assert block.starknet_version is not None
    assert block.l1_gas_price is not None
    assert block.l1_gas_price.price_in_wei > 0

    pending_block = await client_goerli_testnet.get_block_with_txs(
        block_number="pending"
    )

    assert pending_block.starknet_version is not None
    assert pending_block.l1_gas_price is not None
    assert pending_block.l1_gas_price.price_in_wei > 0


@pytest.mark.asyncio
async def test_get_block_with_tx_hashes_new_header_fields(client_goerli_testnet):
    # testing l1_gas_price and starknet_version fields
    block = await client_goerli_testnet.get_block_with_tx_hashes(block_number=800000)

    assert block.starknet_version is not None
    assert block.l1_gas_price is not None
    assert block.l1_gas_price.price_in_wei > 0

    pending_block = await client_goerli_testnet.get_block_with_tx_hashes(
        block_number="pending"
    )

    assert pending_block.starknet_version is not None
    assert pending_block.l1_gas_price is not None
    assert pending_block.l1_gas_price.price_in_wei > 0


@pytest.mark.parametrize(
    "tx_hash, tx_type",
    [
        (
            0x7B31376D1C4F467242616530901E1B441149F1106EF765F202A50A6F917762B,
            DeclareTransactionV3,
        ),
        (
            0x750DC0D6B64D29E7F0CA6399802BA46C6FCA0E37FB977706DFD1DD42B63D757,
            DeployAccountTransactionV3,
        ),
        (
            0x15F2CF38832542602E2D1C8BF0634893E6B43ACB6879E8A8F892F5A9B03C907,
            InvokeTransactionV3,
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_transaction_v3(client_goerli_testnet, tx_hash, tx_type):
    tx = await client_goerli_testnet.get_transaction(tx_hash=tx_hash)
    assert isinstance(tx, tx_type)
    assert tx.version == 3
    assert isinstance(tx.resource_bounds, ResourceBoundsMapping)
    assert tx.paymaster_data == []
    assert tx.tip == 0
    assert tx.nonce_data_availability_mode == DAMode.L1
    assert tx.fee_data_availability_mode == DAMode.L1


@pytest.mark.asyncio
async def test_get_chain_id_sepolia_testnet(client_sepolia_testnet):
    chain_id = await client_sepolia_testnet.get_chain_id()
    assert isinstance(chain_id, str)
    assert chain_id == hex(StarknetChainId.SEPOLIA_TESTNET.value)


@pytest.mark.asyncio
async def test_get_chain_id_sepolia_integration(client_sepolia_integration):
    chain_id = await client_sepolia_integration.get_chain_id()
    assert isinstance(chain_id, str)
    assert chain_id == hex(StarknetChainId.SEPOLIA_INTEGRATION.value)


@pytest.mark.asyncio
async def test_get_events_sepolia_testnet(client_sepolia_testnet):
    events_chunk = await client_sepolia_testnet.get_events(
        address=default_token_address_for_network(SEPOLIA_TESTNET),
        from_block_number=1000,
        to_block_number=1005,
        chunk_size=10,
    )
    assert isinstance(events_chunk, EventsChunk)
    assert len(events_chunk.events) == 10
    assert events_chunk.continuation_token is not None
    assert isinstance(events_chunk.events[0], EmittedEvent)
    assert events_chunk.events[0].block_number == 1000
    assert events_chunk.events[0].block_hash is not None
    assert events_chunk.events[0].from_address is not None
    assert events_chunk.events[0].data is not None
    assert events_chunk.events[0].keys is not None


@pytest.mark.asyncio
async def test_get_tx_receipt_with_execution_resources(client_sepolia_integration):
    receipt = await client_sepolia_integration.get_transaction_receipt(
        tx_hash=0x077E84B7C0C4CC88B778EEAEF32B7CED4500FE4AAEE62FD2F849B7DD90A87826
    )

    assert receipt.execution_resources is not None
    assert receipt.execution_resources.data_availability is not None
    assert receipt.execution_resources.steps is not None
    assert receipt.execution_resources.segment_arena_builtin is not None
    assert receipt.execution_resources.bitwise_builtin_applications is not None
    assert receipt.execution_resources.ec_op_builtin_applications is not None
    assert receipt.execution_resources.memory_holes is not None
    assert receipt.execution_resources.pedersen_builtin_applications is not None
    assert receipt.execution_resources.range_check_builtin_applications is not None


@pytest.mark.asyncio
async def test_get_block_with_receipts(client_goerli_integration):
    block_with_receipts = await client_goerli_integration.get_block_with_receipts(
        block_number=329520
    )

    assert isinstance(block_with_receipts, StarknetBlockWithReceipts)
    assert block_with_receipts.status == BlockStatus.ACCEPTED_ON_L1
    assert len(block_with_receipts.transactions) == 4
    assert all(
        getattr(block_with_receipts, field.name) is not None
        for field in dataclasses.fields(BlockHeader)
    )


@pytest.mark.asyncio
async def test_get_pending_block_with_receipts(client_goerli_integration):
    block_with_receipts = await client_goerli_integration.get_block_with_receipts(
        block_number="pending"
    )

    assert isinstance(block_with_receipts, PendingStarknetBlockWithReceipts)
    assert len(block_with_receipts.transactions) >= 0
    assert all(
        getattr(block_with_receipts, field.name) is not None
        for field in dataclasses.fields(PendingBlockHeader)
    )
