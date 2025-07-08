import dataclasses
import numbers
from unittest.mock import AsyncMock, patch

import pytest

from starknet_py.constants import EXPECTED_RPC_VERSION
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    BlockHeader,
    BlockStatus,
    Call,
    ContractsStorageKeys,
    DAMode,
    DeclareTransactionV3,
    DeployAccountTransactionV3,
    EmittedEvent,
    EstimatedFee,
    EventsChunk,
    InvokeTransactionV3,
    PreConfirmedBlockHeader,
    PreConfirmedStarknetBlockWithReceipts,
    ResourceBounds,
    ResourceBoundsMapping,
    StarknetBlockWithReceipts,
    Transaction,
    TransactionExecutionStatus,
    TransactionFinalityStatus,
    TransactionReceipt,
    TransactionStatus,
)
from starknet_py.net.executable_models import (
    CasmClass,
    Deref,
    Immediate,
    TestLessThan,
    TestLessThanOrEqual,
)
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.http_client import IncompatibleRPCVersionWarning, RpcHttpClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import SEPOLIA, default_token_address_for_network
from starknet_py.tests.e2e.fixtures.constants import (
    EMPTY_CONTRACT_ADDRESS_SEPOLIA,
    MAX_RESOURCE_BOUNDS_SEPOLIA,
    STRK_CLASS_HASH,
    STRK_FEE_CONTRACT_ADDRESS,
)
from starknet_py.transaction_errors import TransactionRevertedError


@pytest.mark.parametrize(
    "transaction_hash",
    (
        "0x016df225d14eb927b1c85ec85d2f9f4fc7653ba13a99e30ffe9e21c96ddc7a6d",  # invoke
        "0x0255f63b1dbd52902e2fb5707d2d2b52d5600fa228f0655b02b78bfcf9cab353",  # declare
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
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA, 0),
        selector=get_selector_from_name("empty"),
        calldata=[0x1, 0x2, 0x3, 0x4, 0x5],
    )
    sign_invoke = await account.sign_invoke_v3(
        calls=call, resource_bounds=MAX_RESOURCE_BOUNDS_SEPOLIA
    )
    invoke = await account.client.send_transaction(sign_invoke)

    with pytest.raises(TransactionRevertedError, match="Input too long for arguments"):
        await account.client.wait_for_tx(tx_hash=invoke.transaction_hash)


@pytest.mark.asyncio
async def test_wait_for_tx_accepted(account_sepolia_testnet):
    account = account_sepolia_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v3(
        calls=call, resource_bounds=MAX_RESOURCE_BOUNDS_SEPOLIA
    )
    invoke = await account.client.send_transaction(sign_invoke)

    result = await account.client.wait_for_tx(tx_hash=invoke.transaction_hash)

    assert result.execution_status == TransactionExecutionStatus.SUCCEEDED
    assert result.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2


@pytest.mark.asyncio
async def test_sign_invoke_v3_auto_estimate(account_sepolia_testnet):
    account = account_sepolia_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v3(calls=call, auto_estimate=True)
    invoke = await account.client.send_transaction(sign_invoke)

    result = await account.client.wait_for_tx(tx_hash=invoke.transaction_hash)

    assert result.execution_status == TransactionExecutionStatus.SUCCEEDED


@pytest.mark.skip("TODO(#1621)")
@pytest.mark.asyncio
async def test_transaction_not_received_max_fee_too_small(account_sepolia_testnet):
    account = account_sepolia_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    resource_bounds = ResourceBoundsMapping(
        l1_gas=ResourceBounds(max_amount=int(1e10), max_price_per_unit=int(1e10)),
        l2_gas=ResourceBounds(max_amount=int(1e10), max_price_per_unit=int(1e10)),
        l1_data_gas=ResourceBounds(max_amount=int(1e10), max_price_per_unit=int(1e10)),
    )
    sign_invoke = await account.sign_invoke_v3(
        calls=call, resource_bounds=resource_bounds
    )

    with pytest.raises(
        ClientError,
        match=r"Client failed with code 55. "
        r"Message: Account validation failed. Data: Max L1Gas price \(\d+\) is lower than the actual gas price: \d+.",
    ):
        await account.client.send_transaction(sign_invoke)


@pytest.mark.skip("TODO(#1621)")
@pytest.mark.asyncio
async def test_transaction_not_received_max_fee_too_big(account_sepolia_testnet):
    account = account_sepolia_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    resource_bounds = ResourceBoundsMapping(
        l1_gas=ResourceBounds(max_amount=int(1e8), max_price_per_unit=int(1e15)),
        l2_gas=ResourceBounds(max_amount=int(1e14), max_price_per_unit=int(1e25)),
        l1_data_gas=ResourceBounds(max_amount=int(1e8), max_price_per_unit=int(1e15)),
    )
    sign_invoke = await account.sign_invoke_v3(
        calls=call, resource_bounds=resource_bounds
    )

    with pytest.raises(
        ClientError,
        match=r"Client failed with code 55. "
        r"Message: Account validation failed\. Data: Resources bounds \(\{.*\}\) exceed balance \(\d+\)\.",
    ):
        await account.client.send_transaction(sign_invoke)


@pytest.mark.asyncio
async def test_transaction_not_received_invalid_nonce(account_sepolia_testnet):
    account = account_sepolia_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v3(
        calls=call, nonce=0, resource_bounds=MAX_RESOURCE_BOUNDS_SEPOLIA
    )

    with pytest.raises(ClientError, match=r".*nonce.*"):
        await account.client.send_transaction(sign_invoke)


@pytest.mark.asyncio
async def test_transaction_not_received_invalid_signature(account_sepolia_testnet):
    account = account_sepolia_testnet
    call = Call(
        to_addr=int(EMPTY_CONTRACT_ADDRESS_SEPOLIA, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_v3(
        calls=call, resource_bounds=MAX_RESOURCE_BOUNDS_SEPOLIA
    )
    sign_invoke = dataclasses.replace(sign_invoke, signature=[0x21, 0x37])
    with pytest.raises(
        ClientError,
        match=r"Account validation failed",
    ) as exc:
        await account.client.send_transaction(sign_invoke)

    assert exc.value.data is not None
    assert "Data:" in exc.value.message


# TODO (#1219): move tests below to full_node_test.py
@pytest.mark.asyncio
async def test_estimate_message_fee(client_sepolia_testnet):
    client = client_sepolia_testnet
    # info about this message from
    # https://sepolia.starkscan.co/message-log/0x061e8c5211c705d0ab608e42f181edf4ef9ae891b3e568a6fe1c3b83076eefc2_0_1
    estimated_message = await client.estimate_message_fee(
        from_address="0x18e4a8e2badb5f5950758f46f8108e2c5d357b07",
        block_number=51569,
        to_address="0x054f677f3e952d023e2f31d74606270b676eaf493befbcfa2111f2b96a242362",
        entry_point_selector="0x03fa70707d0e831418fb142ca8fb7483611b84e89c0c42bf1fc2a7a5c40890ad",
        payload=[
            "0x1b0b3ddfc5264c441c9eee709011a863",
            "0xfbe265a54523fc9070e26bfc5aa145ab",
            "0x5469d9",
            "0x0",
        ],
    )

    assert isinstance(estimated_message, EstimatedFee)
    assert all(
        getattr(estimated_message, field.name) >= 0
        for field in dataclasses.fields(EstimatedFee)
        if isinstance(getattr(estimated_message, field.name), numbers.Number)
    )
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
            block_number=51569,
            to_address="0x054f677f3e952d023e2f31d74606270b676eaf493befbcfa2111f2b96a242362",
            entry_point_selector="0x03fa70707d0e831418fb142ca8fb7483611b84e89c0c42bf1fc2a7a5c40890ad",
            payload=[
                "0x1b0b3ddfc5264c441c9eee709011a863",
                "0xfbe265a54523fc9070e26bfc5aa145ab",
                "0x5469d9",
                "0x0",
            ],
        )


@pytest.mark.parametrize(
    "from_address, to_address",
    (
        (
            "0xbe1259ff905cadbbaa62514388b71bdefb8aacc1",
            "0x1234",
        ),  # valid `from_address`, invalid `to_address`
        (
            "0xDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",
            "0x06524771cb912945bf2db355b5a12355ca2e2ff05e15ee35366336a602293f2d",
        ),  # invalid `from_address` (passes through assert), valid `to_address`
    ),
)
@pytest.mark.asyncio
async def test_estimate_message_fee_throws(
    client_sepolia_testnet, from_address, to_address
):
    with pytest.raises(ClientError):
        _ = await client_sepolia_testnet.estimate_message_fee(
            block_number=80000,
            from_address=from_address,
            to_address=to_address,
            entry_point_selector="0x3248",
            payload=[
                "0x4359",
            ],
        )


@pytest.mark.asyncio
async def test_get_tx_receipt_reverted(client_sepolia_testnet):
    reverted_tx_hash = (
        "0x00fecca6a328dd11f40b79c30fe22d23bc6975d1a0923a95b90aff4016a84333"
    )

    res = await client_sepolia_testnet.get_transaction_receipt(tx_hash=reverted_tx_hash)

    assert res.execution_status == TransactionExecutionStatus.REVERTED
    assert res.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L1
    assert "Got an exception while executing a hint" in res.revert_reason


@pytest.mark.parametrize(
    "block_number, index, expected_hash",
    [
        (81116, 0, 0x38FC01353196AEEBA62C74A8C8479FFF94AAA8CD4C3655782D49D755BBE63A8),
        (81116, 26, 0x3F873FE2CC884A88B8D4378EAC1786145F7167D61B0A9442DA15B0181582522),
        (80910, 23, 0x67C1E282F64DAD5682B1F377A5FDA1778311D894B2EE47A06058790A8B08460),
    ],
)
@pytest.mark.asyncio
async def test_get_transaction_by_block_id_and_index(
    client_sepolia_testnet, block_number, index, expected_hash
):
    tx = await client_sepolia_testnet.get_transaction_by_block_id(
        block_number=block_number, index=index
    )

    assert isinstance(tx, Transaction)
    assert tx.hash == expected_hash


@pytest.mark.asyncio
async def test_get_l1_message_hash(client_sepolia_testnet):
    tx_hash = "0x067d959200d65d4ad293aa4b0da21bb050a1f669bce37d215c6edbf041269c07"
    l1_message_hash = await client_sepolia_testnet.get_l1_message_hash(tx_hash)
    assert (
        hex(l1_message_hash)
        == "0x2e350fa9d830482605cb68be4fdb9f0cb3e1f95a0c51623ac1a5d1bd997c2090"
    )


@pytest.mark.asyncio
async def test_get_l1_message_hash_raises_on_incorrect_transaction_type(
    client_sepolia_testnet,
):
    tx_hash = "0x38FC01353196AEEBA62C74A8C8479FFF94AAA8CD4C3655782D49D755BBE63A8"
    with pytest.raises(
        TypeError, match=f"Transaction {tx_hash} is not a result of L1->L2 interaction."
    ):
        await client_sepolia_testnet.get_l1_message_hash(tx_hash)


@pytest.mark.asyncio
async def test_spec_version(client_sepolia_testnet):
    spec_version = await client_sepolia_testnet.spec_version()

    assert spec_version is not None
    assert isinstance(spec_version, str)


@pytest.mark.asyncio
async def test_get_transaction_status(client_sepolia_testnet):
    tx_status = await client_sepolia_testnet.get_transaction_status(
        tx_hash=0x06BF304EFEF9D0D28161C69A4660FA8AC769118A81FACE53BC8EA165BBB3F86F
    )

    assert tx_status.finality_status == TransactionStatus.ACCEPTED_ON_L1
    assert tx_status.execution_status == TransactionExecutionStatus.SUCCEEDED


@pytest.mark.asyncio
async def test_get_transaction_status_with_failure_reason(client_sepolia_testnet):
    # TODO(#1498): Potentially change tx for one that has a known failure reason
    # Originally, tx with hash 0x048d0e94d643f54f517271bd54936aa958d787c1b5d9d0a013ece6868ba9c8b7
    # has an unknown failure reason, therefore we need to mock it.
    with patch(
        f"{RpcHttpClient.__module__}.RpcHttpClient.call", AsyncMock()
    ) as mocked_tx_status_call_rpc:
        return_value = {
            "execution_status": "REVERTED",
            "finality_status": "ACCEPTED_ON_L2",
            "failure_reason": "Some failure reason",
        }
        mocked_tx_status_call_rpc.return_value = return_value

        tx_status = await client_sepolia_testnet.get_transaction_status(
            tx_hash=0x048D0E94D643F54F517271BD54936AA958D787C1B5D9D0A013ECE6868BA9C8B7
        )

        assert tx_status.finality_status == TransactionStatus.ACCEPTED_ON_L2
        assert tx_status.execution_status == TransactionExecutionStatus.REVERTED
        assert tx_status.failure_reason == "Some failure reason"


@pytest.mark.skip("TODO(#1621)")
@pytest.mark.asyncio
async def test_get_block_new_header_fields(client_sepolia_testnet):
    # testing l1_gas_price and starknet_version fields
    block = await client_sepolia_testnet.get_block_with_txs(block_number=155)

    assert block.starknet_version is not None
    assert block.l1_gas_price is not None
    assert block.l1_gas_price.price_in_wei > 0

    pre_confirmed_block = await client_sepolia_testnet.get_block_with_txs(
        block_number="pre_confirmed"
    )

    assert pre_confirmed_block.starknet_version is not None
    assert pre_confirmed_block.l1_gas_price is not None
    assert pre_confirmed_block.l1_gas_price.price_in_wei > 0


@pytest.mark.skip("TODO(#1621)")
@pytest.mark.asyncio
async def test_get_block_with_tx_hashes_new_header_fields(client_sepolia_testnet):
    # testing l1_gas_price and starknet_version fields
    block = await client_sepolia_testnet.get_block_with_tx_hashes(block_number=155)

    assert block.starknet_version is not None
    assert block.l1_gas_price is not None
    assert block.l1_gas_price.price_in_wei > 0

    pre_confirmed_block = await client_sepolia_testnet.get_block_with_tx_hashes(
        block_number="pre_confirmed"
    )

    assert pre_confirmed_block.starknet_version is not None
    assert pre_confirmed_block.l1_gas_price is not None
    assert pre_confirmed_block.l1_gas_price.price_in_wei > 0


@pytest.mark.parametrize(
    "tx_hash, tx_type",
    [
        (
            0x054270D103C875A613E013D1FD555EDCFF2085FECA9D7B4532243A8257FD5CF3,
            DeclareTransactionV3,
        ),
        (
            0x06718B783A0B888F5421C4EB76A532FEB9FD5167B2B09274298F79798C782B32,
            DeployAccountTransactionV3,
        ),
        (
            0x043868D939FA1B62B977FFFC659146688E954BBABEDA020CC99BAE1C220E4882,
            InvokeTransactionV3,
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_transaction_v3(client_sepolia_testnet, tx_hash, tx_type):
    tx = await client_sepolia_testnet.get_transaction(tx_hash=tx_hash)
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
    assert chain_id == hex(StarknetChainId.SEPOLIA.value)


@pytest.mark.asyncio
async def test_get_events_sepolia_testnet(client_sepolia_testnet):
    events_chunk = await client_sepolia_testnet.get_events(
        address=default_token_address_for_network(SEPOLIA),
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
async def test_get_block_with_receipts(client_sepolia_testnet):
    block_with_receipts = await client_sepolia_testnet.get_block_with_receipts(
        block_number=48778
    )

    assert isinstance(block_with_receipts, StarknetBlockWithReceipts)
    assert block_with_receipts.status == BlockStatus.ACCEPTED_ON_L1
    assert len(block_with_receipts.transactions) == 43
    assert all(
        getattr(block_with_receipts, field.name) is not None
        for field in dataclasses.fields(BlockHeader)
    )


@pytest.mark.skip("TODO(#1621)")
@pytest.mark.asyncio
async def test_get_pre_confirmed_block_with_receipts(client_sepolia_testnet):
    block_with_receipts = await client_sepolia_testnet.get_block_with_receipts(
        block_number="pre_confirmed"
    )

    assert isinstance(block_with_receipts, PreConfirmedStarknetBlockWithReceipts)
    assert len(block_with_receipts.transactions) >= 0
    assert all(
        getattr(block_with_receipts, field.name) is not None
        for field in dataclasses.fields(PreConfirmedBlockHeader)
    )


@pytest.mark.asyncio
async def test_get_storage_proof(client_sepolia_testnet):
    # Nodes don't support storage proofs for blocks that are too far in the past, hence we need to get last block number
    block_number = await client_sepolia_testnet.get_block_number()
    storage_proof = await client_sepolia_testnet.get_storage_proof(
        block_number=block_number,
        contract_addresses=[int(STRK_FEE_CONTRACT_ADDRESS, 16)],
        contracts_storage_keys=[
            ContractsStorageKeys(
                contract_address=int(STRK_FEE_CONTRACT_ADDRESS, 16),
                storage_keys=[int("0x45524332305f62616c616e636573", 16)],
            )
        ],
        class_hashes=[int(STRK_CLASS_HASH, 16)],
    )

    # We can't check exact values, as they change over the time
    assert len(storage_proof.classes_proof) > 0
    assert len(storage_proof.contracts_proof.nodes) > 0
    assert len(storage_proof.contracts_storage_proofs[0]) > 16


@pytest.mark.asyncio
async def test_get_compiled_casm(client_sepolia_testnet):
    compiled_casm = await client_sepolia_testnet.get_compiled_casm(
        class_hash=int(STRK_CLASS_HASH, 16)
    )

    assert isinstance(compiled_casm, CasmClass)
    assert len(compiled_casm.bytecode) == 20477
    assert len(compiled_casm.hints) == 931

    first_hint = compiled_casm.hints[0][1][0]
    assert isinstance(first_hint, TestLessThanOrEqual)
    assert first_hint.test_less_than_or_equal.dst.offset == 0
    assert first_hint.test_less_than_or_equal.dst.register == "AP"
    assert isinstance(first_hint.test_less_than_or_equal.lhs, Immediate)
    assert first_hint.test_less_than_or_equal.lhs.immediate == 0
    assert isinstance(first_hint.test_less_than_or_equal.rhs, Deref)
    assert first_hint.test_less_than_or_equal.rhs.deref.offset == -6
    assert first_hint.test_less_than_or_equal.rhs.deref.register == "FP"

    second_hint = compiled_casm.hints[1][1][0]
    assert isinstance(second_hint, TestLessThan)
    assert second_hint.test_less_than.dst.offset == 4
    assert second_hint.test_less_than.dst.register == "AP"
    assert isinstance(second_hint.test_less_than.lhs, Deref)
    assert second_hint.test_less_than.lhs.deref.offset == -1
    assert second_hint.test_less_than.lhs.deref.register == "AP"
    assert isinstance(second_hint.test_less_than.rhs, Immediate)
    assert (
        second_hint.test_less_than.rhs.immediate
        == 0x800000000000000000000000000000000000000000000000000000000000000
    )


@pytest.mark.asyncio
async def test_warning_on_incompatible_node_spec_version(client_sepolia_testnet):
    old_rpc_url = client_sepolia_testnet.url.replace("v0_8", "v0_7")
    node = FullNodeClient(old_rpc_url)

    pattern = (
        rf"RPC node with the url {old_rpc_url} uses incompatible version 0\.8\.1\. "
        rf"Expected version: {EXPECTED_RPC_VERSION}"
    )
    with pytest.warns(IncompatibleRPCVersionWarning, match=pattern):
        await node.get_chain_id()
