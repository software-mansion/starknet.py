import dataclasses
import sys

import pytest

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    Call,
    DAMode,
    DeclareTransactionV3,
    DeployAccountTransactionV3,
    EstimatedFee,
    EventsChunk,
    InvokeTransactionV3,
    ResourceBoundsMapping,
    TransactionExecutionStatus,
    TransactionFinalityStatus,
    TransactionReceipt,
    TransactionStatus,
)
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import SEPOLIA_TESTNET, default_token_address_for_network
from starknet_py.tests.e2e.fixtures.constants import (
    EMPTY_CONTRACT_ADDRESS_GOERLI_TESTNET,
)
from starknet_py.transaction_errors import TransactionRevertedError


@pytest.mark.parametrize(
    "transaction_hash",
    (
        "0x06d11fa74255c1f86aace54cbf382ab8c89e2b90fb0801f751834ca52bf2a2a2",  # invoke
        "0x7c671df75d664b191a8fd227996eb0de7557bcde81f3d618c58cf808d7efbc4",  # declare
        "0x510fa73cdb49ae81742441c494c396883a2eee91209fe387ce1dec5fa04ecb",  # deploy
        "0x6e882ef88d8767046e64a1b450a29f18b086121b38658d3431605d27251fa1d",  # deploy_account
        "0x60bd50c38082211e6aedb21838fe7402a67216d559d9a4848e6c5e9670c90e",  # l1_handler
    ),
)
@pytest.mark.asyncio
async def test_get_transaction_receipt(client_goerli_integration, transaction_hash):
    receipt = await client_goerli_integration.get_transaction_receipt(
        tx_hash=transaction_hash
    )

    assert isinstance(receipt, TransactionReceipt)
    assert receipt.execution_status is not None
    assert receipt.finality_status is not None
    assert receipt.execution_resources is not None
    assert receipt.type is not None


@pytest.mark.asyncio
async def test_wait_for_tx_reverted(account_goerli_testnet):
    account = account_goerli_testnet
    # Calldata too long for the function (it has no parameters) to trigger REVERTED status
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_GOERLI_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[0x1, 0x2, 0x3, 0x4, 0x5],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=int(1e16))
    invoke = await account.client.send_transaction(sign_invoke)

    with pytest.raises(TransactionRevertedError, match="Input too long for arguments"):
        await account.client.wait_for_tx(tx_hash=invoke.transaction_hash)


@pytest.mark.asyncio
async def test_wait_for_tx_accepted(account_goerli_testnet):
    account = account_goerli_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_GOERLI_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=int(1e16))
    invoke = await account.client.send_transaction(sign_invoke)

    result = await account.client.wait_for_tx(tx_hash=invoke.transaction_hash)

    assert result.execution_status == TransactionExecutionStatus.SUCCEEDED
    assert result.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2


@pytest.mark.asyncio
async def test_transaction_not_received_max_fee_too_small(account_goerli_testnet):
    account = account_goerli_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_GOERLI_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=int(1e10))

    with pytest.raises(ClientError, match=r".*Max fee.*"):
        await account.client.send_transaction(sign_invoke)


@pytest.mark.asyncio
async def test_transaction_not_received_max_fee_too_big(account_goerli_testnet):
    account = account_goerli_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_GOERLI_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=sys.maxsize)

    with pytest.raises(ClientError, match=r".*max_fee.*"):
        await account.client.send_transaction(sign_invoke)


@pytest.mark.asyncio
async def test_transaction_not_received_invalid_nonce(account_goerli_testnet):
    account = account_goerli_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_GOERLI_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=int(1e16), nonce=0)

    with pytest.raises(ClientError, match=r".*nonce.*"):
        await account.client.send_transaction(sign_invoke)


@pytest.mark.asyncio
async def test_transaction_not_received_invalid_signature(account_goerli_testnet):
    account = account_goerli_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_GOERLI_TESTNET, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v1(calls=call, max_fee=int(1e16))
    sign_invoke = dataclasses.replace(sign_invoke, signature=[0x21, 0x37])

    with pytest.raises(ClientError, match=r"Signature.*is invalid") as exc:
        await account.client.send_transaction(sign_invoke)

    assert exc.value.data is not None
    assert "Data:" in exc.value.message


# TODO (#1219): move tests below to full_node_test.py


@pytest.mark.asyncio
async def test_estimate_message_fee(client_goerli_integration):
    client = client_goerli_integration

    # info about this message from
    # https://integration.starkscan.co/message/0x140185c79e5a04c7c3fae513001f358beb66653dcee75be38f05bd30adba85dd
    estimated_message = await client.estimate_message_fee(
        block_number=306687,
        from_address="0xbe1259ff905cadbbaa62514388b71bdefb8aacc1",
        to_address="0x073314940630fd6dcda0d772d4c972c4e0a9946bef9dabf4ef84eda8ef542b82",
        entry_point_selector="0x02d757788a8d8d6f21d1cd40bce38a8222d70654214e96ff95d8086e684fbee5",
        payload=[
            "0x54d01e5fc6eb4e919ceaab6ab6af192e89d1beb4f29d916768c61a4d48e6c95",
            "0x38d7ea4c68000",
            "0x0",
        ],
    )

    assert isinstance(estimated_message, EstimatedFee)
    assert estimated_message.overall_fee > 0
    assert estimated_message.gas_price > 0
    assert estimated_message.gas_consumed > 0
    assert estimated_message.unit is not None


@pytest.mark.asyncio
async def test_estimate_message_fee_invalid_eth_address_assertion_error(
    client_goerli_integration,
):
    client = client_goerli_integration
    invalid_eth_address = "0xD"

    # info about this message from
    # https://integration.starkscan.co/message/0x140185c79e5a04c7c3fae513001f358beb66653dcee75be38f05bd30adba85dd
    with pytest.raises(
        AssertionError,
        match=f"Argument 'from_address': {invalid_eth_address} is not a valid Ethereum address.",
    ):
        _ = await client.estimate_message_fee(
            from_address=invalid_eth_address,
            block_number=306687,
            to_address="0x073314940630fd6dcda0d772d4c972c4e0a9946bef9dabf4ef84eda8ef542b82",
            entry_point_selector="0x02d757788a8d8d6f21d1cd40bce38a8222d70654214e96ff95d8086e684fbee5",
            payload=[
                "0x54d01e5fc6eb4e919ceaab6ab6af192e89d1beb4f29d916768c61a4d48e6c95",
                "0x38d7ea4c68000",
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
    client_goerli_integration, from_address, to_address
):
    client = client_goerli_integration

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
async def test_get_tx_receipt_reverted(client_goerli_integration):
    client = client_goerli_integration
    reverted_tx_hash = (
        "0x4a3c389816f8544d05db964957eb41a9e3f8c660e8487695cb75438ef983181"
    )

    res = await client.get_transaction_receipt(tx_hash=reverted_tx_hash)

    assert res.execution_status == TransactionExecutionStatus.REVERTED
    assert res.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L1
    assert "Input too long for arguments" in res.revert_reason


@pytest.mark.parametrize(
    "block_number, transaction_index",
    [
        # declare: https://integration.voyager.online/tx/0x6d8c9f8806bda9a3279bcc69e8461ed21b4f3ce9e087ae02d5368d0c9d63c57
        (307145, 0),
        # deploy: https://integration.voyager.online/tx/0x510fa73cdb49ae81742441c494c396883a2eee91209fe387ce1dec5fa04ecb
        (248061, 0),
        # deploy_account: https://integration.voyager.online/tx/0x593c073960140ab7af7951fadb6a129572cc504ef0b9107992c5c1efe5a0fb5
        (307054, 1),
        # invoke: https://integration.voyager.online/tx/0x6225b92ce88603645e42fc4b664034f788ec9f01a5aadd9855646dd721898e5
        (307163, 0),
        # l1_handler: https://integration.voyager.online/tx/0x66e2db10edbed4b262e01ee0f89ff77907f9ca1b4fe11603d691f16370248f7
        (307061, 3),
    ],
)
@pytest.mark.asyncio
async def test_get_transaction_by_block_id_and_index(
    client_goerli_integration, block_number, transaction_index
):
    client = client_goerli_integration

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


@pytest.mark.asyncio
async def test_get_tx_receipt_new_fields(client_goerli_testnet):
    l1_handler_tx_hash = (
        0xBEFE411182979262478CA8CA73BED724237D03D303CE420D94DE7664A78347
    )
    receipt = await client_goerli_testnet.get_transaction_receipt(
        tx_hash=l1_handler_tx_hash
    )

    assert receipt.execution_resources is not None


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
