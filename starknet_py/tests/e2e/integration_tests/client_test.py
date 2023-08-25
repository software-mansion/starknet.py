import dataclasses
import sys

import pytest

from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import (
    Call,
    EstimatedFee,
    SignatureOnStateDiff,
    StateUpdateWithBlock,
    TransactionExecutionStatus,
    TransactionFinalityStatus,
    TransactionReceipt,
)
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.tests.e2e.fixtures.constants import (
    PREDEPLOYED_EMPTY_CONTRACT_ADDRESS,
    PREDEPLOYED_MAP_CONTRACT_ADDRESS,
)
from starknet_py.transaction_errors import (
    TransactionRejectedError,
    TransactionRevertedError,
)


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
async def test_get_transaction_receipt(client_integration, transaction_hash):
    receipt = await client_integration.get_transaction_receipt(tx_hash=transaction_hash)

    assert isinstance(receipt, TransactionReceipt)
    assert receipt.execution_status is not None
    assert receipt.finality_status is not None


# There is a chance that the full node test fails with a reason: "Transaction with the same hash already exists
# in the mempool" (or something like that). This is because gateway has instant access to pending nodes, but nodes
# do not. If, somehow, gateway test gets executed before the full_node one, the transaction will still be in the PENDING
# block and the next one with the same hash will be rejected (you could artificially add more items to 'calldata' array,
# but you would need to change the nonce and tests depending on each other is a bad idea).
# Same thing could happen when you run tests locally and then push to run them on CI.
@pytest.mark.skipif(
    condition="--client=gateway" in sys.argv,
    reason="Separate FullNode tests from Gateway ones.",
)
@pytest.mark.asyncio
async def test_wait_for_tx_reverted_full_node(full_node_account_integration):
    account = full_node_account_integration
    # Calldata too long for the function (it has no parameters) to trigger REVERTED status
    call = Call(
        to_addr=int(PREDEPLOYED_EMPTY_CONTRACT_ADDRESS, 0),
        selector=get_selector_from_name("empty"),
        calldata=[0x1, 0x2, 0x3, 0x4, 0x5],
    )
    sign_invoke = await account.sign_invoke_transaction(calls=call, max_fee=int(1e16))
    invoke = await account.client.send_transaction(sign_invoke)

    with pytest.raises(TransactionRevertedError, match=r".*reverted.*"):
        await account.client.wait_for_tx(tx_hash=invoke.transaction_hash)


@pytest.mark.skipif(
    condition="--client=full_node" in sys.argv,
    reason="Separate FullNode tests from Gateway ones.",
)
@pytest.mark.asyncio
async def test_wait_for_tx_reverted_gateway(gateway_account_integration):
    account = gateway_account_integration
    # Calldata too long for the function (it has no parameters) to trigger REVERTED status
    call = Call(
        to_addr=int(PREDEPLOYED_EMPTY_CONTRACT_ADDRESS, 0),
        selector=get_selector_from_name("empty"),
        calldata=[0x1, 0x2, 0x3, 0x4, 0x5],
    )
    sign_invoke = await account.sign_invoke_transaction(calls=call, max_fee=int(1e16))
    invoke = await account.client.send_transaction(sign_invoke)

    with pytest.raises(TransactionRevertedError, match="Input too long for arguments"):
        await account.client.wait_for_tx(tx_hash=invoke.transaction_hash)


# No same test for full_node, because nodes don't know about rejected transactions
# https://community.starknet.io/t/efficient-utilization-of-sequencer-capacity-in-starknet-v0-12-1/95607#api-changes-3
@pytest.mark.skipif(
    condition="--client=full_node" in sys.argv,
    reason="Separate FullNode tests from Gateway ones.",
)
@pytest.mark.asyncio
async def test_wait_for_tx_rejected_gateway(gateway_account_integration):
    account = gateway_account_integration
    call = Call(
        to_addr=int(PREDEPLOYED_MAP_CONTRACT_ADDRESS, 0),
        selector=get_selector_from_name("put"),
        calldata=[0x102, 0x125],
    )
    call2 = Call(
        to_addr=int(
            "0x05cd21d6b3952a869fda11fa9a5bd2657bd68080d3da255655ded47a81c8bd53", 0
        ),
        selector=get_selector_from_name("put"),
        calldata=[0x103, 0x126],
    )
    sign_invoke = await account.sign_invoke_transaction(calls=call, max_fee=int(1e16))
    sign_invoke2 = await account.sign_invoke_transaction(calls=call2, max_fee=int(1e16))
    # same nonces to trigger REJECTED error
    assert sign_invoke2.nonce == sign_invoke.nonce

    # this one should pass
    invoke = await account.client.send_transaction(sign_invoke)
    # this should be rejected
    invoke2 = await account.client.send_transaction(sign_invoke2)

    with pytest.raises(TransactionRejectedError):
        _ = await account.client.wait_for_tx(tx_hash=invoke2.transaction_hash)

    invoke2_receipt = await account.client.get_transaction_receipt(
        tx_hash=invoke2.transaction_hash
    )

    assert invoke2_receipt.execution_status == TransactionExecutionStatus.REJECTED


# Same here as in comment above 'test_wait_for_tx_reverted_full_node'
@pytest.mark.skipif(
    condition="--client=gateway" in sys.argv,
    reason="Separate FullNode tests from Gateway ones.",
)
@pytest.mark.asyncio
async def test_wait_for_tx_full_node_accepted(full_node_account_integration):
    account = full_node_account_integration
    call = Call(
        to_addr=int(PREDEPLOYED_EMPTY_CONTRACT_ADDRESS, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_transaction(calls=call, max_fee=int(1e16))
    invoke = await account.client.send_transaction(sign_invoke)

    result = await account.client.wait_for_tx(tx_hash=invoke.transaction_hash)

    assert result.execution_status == TransactionExecutionStatus.SUCCEEDED
    assert result.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2


@pytest.mark.skipif(
    condition="--client=full_node" in sys.argv,
    reason="Separate FullNode tests from Gateway ones.",
)
@pytest.mark.asyncio
async def test_wait_for_tx_gateway_accepted(gateway_account_integration):
    account = gateway_account_integration
    call = Call(
        to_addr=int(PREDEPLOYED_EMPTY_CONTRACT_ADDRESS, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_transaction(calls=call, max_fee=int(1e16))
    invoke = await account.client.send_transaction(sign_invoke)

    result = await account.client.wait_for_tx(tx_hash=invoke.transaction_hash)

    assert result.execution_status == TransactionExecutionStatus.SUCCEEDED
    assert result.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L2


@pytest.mark.asyncio
async def test_transaction_not_received_max_fee_too_small(account_integration):
    account = account_integration
    call = Call(
        to_addr=int(PREDEPLOYED_EMPTY_CONTRACT_ADDRESS, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    ARBITRARILY_SMALL_NONCE = 1
    sign_invoke = await account.sign_invoke_transaction(
        calls=call, max_fee=ARBITRARILY_SMALL_NONCE
    )

    with pytest.raises(ClientError, match=r".*Max fee.*"):
        _ = await account.client.send_transaction(sign_invoke)


@pytest.mark.asyncio
async def test_transaction_not_received_max_fee_too_big(account_integration):
    account = account_integration
    call = Call(
        to_addr=int(PREDEPLOYED_EMPTY_CONTRACT_ADDRESS, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    ARBITRARILY_BIG_FEE_WE_WILL_NEVER_HAVE_SO_MUCH_ETH = sys.maxsize
    sign_invoke = await account.sign_invoke_transaction(
        calls=call, max_fee=ARBITRARILY_BIG_FEE_WE_WILL_NEVER_HAVE_SO_MUCH_ETH
    )

    with pytest.raises(ClientError, match=r".*max_fee.*"):
        _ = await account.client.send_transaction(sign_invoke)


@pytest.mark.asyncio
async def test_transaction_not_received_invalid_nonce(account_integration):
    account = account_integration
    call = Call(
        to_addr=int(PREDEPLOYED_EMPTY_CONTRACT_ADDRESS, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_transaction(
        calls=call, max_fee=int(1e16), nonce=0
    )

    with pytest.raises(ClientError, match=r".*nonce.*"):
        _ = await account.client.send_transaction(sign_invoke)


@pytest.mark.asyncio
async def test_transaction_not_received_invalid_signature(account_integration):
    account = account_integration
    call = Call(
        to_addr=int(PREDEPLOYED_EMPTY_CONTRACT_ADDRESS, 0),
        selector=get_selector_from_name("empty"),
        calldata=[],
    )
    sign_invoke = await account.sign_invoke_transaction(calls=call, max_fee=int(1e16))
    sign_invoke = dataclasses.replace(sign_invoke, signature=[0x21, 0x37])

    # first one for gateway, second for pathfinder node
    with pytest.raises(ClientError, match=r"(.*Signature.*)|(.*An unexpected error.*)"):
        _ = await account.client.send_transaction(sign_invoke)


# ------------------------------------ FULL_NODE_CLIENT TESTS ------------------------------------

# TODO (#1142): move tests below to full_node_test.py once devnet releases rust version supporting RPC v0.4.0


@pytest.mark.skipif(
    condition="--client=gateway" in sys.argv,
    reason="Separate FullNode tests from Gateway ones.",
)
@pytest.mark.asyncio
async def test_estimate_message_fee(full_node_client_integration):
    client = full_node_client_integration

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
    assert estimated_message.gas_usage > 0


@pytest.mark.skipif(
    condition="--client=gateway" in sys.argv,
    reason="Separate FullNode tests from Gateway ones.",
)
@pytest.mark.asyncio
async def test_estimate_message_fee_invalid_eth_address_assertion_error(
    full_node_client_integration,
):
    client = full_node_client_integration
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


@pytest.mark.skipif(
    condition="--client=gateway" in sys.argv,
    reason="Separate FullNode tests from Gateway ones.",
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
    full_node_client_integration, from_address, to_address
):
    client = full_node_client_integration

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
async def test_get_tx_receipt_reverted(client_integration):
    client = client_integration
    reverted_tx_hash = (
        "0x4a3c389816f8544d05db964957eb41a9e3f8c660e8487695cb75438ef983181"
    )

    res = await client.get_transaction_receipt(tx_hash=reverted_tx_hash)

    assert res.execution_status == TransactionExecutionStatus.REVERTED
    assert res.finality_status == TransactionFinalityStatus.ACCEPTED_ON_L1
    if isinstance(client, GatewayClient):
        assert "Input too long for arguments" in res.revert_error
    else:
        assert "Input too long for arguments" in res.revert_reason


@pytest.mark.skipif(
    condition="--client=gateway" in sys.argv,
    reason="Separate FullNode tests from Gateway ones.",
)
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
    full_node_client_integration, block_number, transaction_index
):
    client = full_node_client_integration

    tx = await client.get_transaction_by_block_id(
        block_number=block_number, index=transaction_index
    )

    assert tx.hash is not None

    receipt = await client.get_transaction_receipt(tx_hash=tx.hash)

    assert receipt.finality_status is not None
    assert receipt.execution_status is not None


@pytest.mark.skipif(
    condition="--client=gateway" in sys.argv,
    reason="Separate FullNode tests from Gateway ones.",
)
@pytest.mark.asyncio
async def test_get_pending_transactions(full_node_client_integration):
    client = full_node_client_integration
    res = await client.get_pending_transactions()

    for tx in res:
        assert tx.hash is not None


@pytest.mark.asyncio
async def test_get_block(full_node_client_integration):
    client = full_node_client_integration
    res = await client.get_block(block_number="latest")

    for tx in res.transactions:
        assert tx.hash is not None


@pytest.mark.asyncio
async def test_get_public_key(gateway_client_integration):
    current_public_key = (
        "0x52934be54ce926b1e715f15dc2542849a97ecfdf829cd0b7384c64eeeb2264e"
    )
    public_key = await gateway_client_integration.get_public_key()

    assert isinstance(public_key, str)
    assert public_key == current_public_key


@pytest.mark.asyncio
async def test_get_signature(gateway_client_integration):
    block_number = 100000
    signature = await gateway_client_integration.get_signature(
        block_number=block_number
    )
    block = await gateway_client_integration.get_block(block_number=block_number)

    assert isinstance(signature, SignatureOnStateDiff)
    assert signature.block_number == block_number
    assert len(signature.signature) == 2
    assert signature.signature_input.block_hash == block.block_hash


@pytest.mark.asyncio
async def test_get_state_update_with_block(gateway_client_integration):
    res = await gateway_client_integration.get_state_update(
        block_number=100000, include_block=True
    )
    block = await gateway_client_integration.get_block(block_number=100000)

    assert isinstance(res, StateUpdateWithBlock)

    assert res.block == block
    assert res.state_update is not None


# TODO (#1166): remove tests below after mainnet release
@pytest.mark.asyncio
async def test_get_block_different_starknet_versions():
    mainnet = GatewayClient(net="mainnet")
    testnet = GatewayClient(net="testnet")

    _ = await mainnet.get_block(block_number=100000)
    _ = await testnet.get_block(block_number=100000)


@pytest.mark.asyncio
async def test_get_state_update_different_starknet_versions():
    mainnet = GatewayClient(net="mainnet")
    testnet = GatewayClient(net="testnet")

    _ = await mainnet.get_state_update(block_number=100000)

    with pytest.raises(ValueError):
        _ = await mainnet.get_state_update(block_number=100000, include_block=False)
        _ = await mainnet.get_state_update(block_number=100000, include_block=True)

    _ = await testnet.get_state_update(block_number=100000, include_block=True)
