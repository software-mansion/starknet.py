import pytest

from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import EstimatedFee, TransactionReceipt
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.gateway_client import GatewayClient

INTEGRATION_NODE_URL = "http://188.34.188.184:9545/rpc/v0.4"
INTEGRATION_GATEWAY_URL = "https://external.integration.starknet.io"

full_node_client = FullNodeClient(node_url=INTEGRATION_NODE_URL)
gateway_client = GatewayClient(net=INTEGRATION_GATEWAY_URL)


@pytest.mark.parametrize(
    "client",
    (
        full_node_client,
        gateway_client,
    ),
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
async def test_get_transaction_receipt(client, transaction_hash):
    receipt = await client.get_transaction_receipt(tx_hash=transaction_hash)

    assert isinstance(receipt, TransactionReceipt)
    assert receipt.execution_status is not None
    assert receipt.finality_status is not None


# ------------------------------------ FULL_NODE_CLIENT TESTS ------------------------------------

# TODO move tests below to full_node_test.py once devnet releases rust version supporting RPC v0.4.0


@pytest.mark.asyncio
async def test_estimate_message_fee():
    client = full_node_client

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


@pytest.mark.asyncio
async def test_estimate_message_fee_invalid_eth_address():
    client = full_node_client
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
async def test_estimate_message_fee_throws(from_address, to_address):
    client = full_node_client

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
