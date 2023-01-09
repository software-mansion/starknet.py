import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.client_models import Call
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId, parse_address
from starknet_py.net.networks import MAINNET, TESTNET, TESTNET2
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE
from starknet_py.transaction_exceptions import TransactionRejectedError


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_balance_throws_when_token_not_specified(account_client):
    with pytest.raises(
        ValueError,
        match="Argument token_address must be specified when using a custom net address",
    ):
        await account_client.get_balance()


@pytest.mark.asyncio
async def test_balance_when_token_specified(account_client, erc20_contract):
    balance = await account_client.get_balance(erc20_contract.address)

    assert balance == 200


@pytest.mark.asyncio
@pytest.mark.parametrize("net", (TESTNET, TESTNET2, MAINNET))
async def test_get_balance_default_token_address(net):
    client = GatewayClient(net=net)
    acc_client = AccountClient(
        client=client,
        address="0x123",
        key_pair=KeyPair(123, 456),
        chain=StarknetChainId.TESTNET,
    )

    with patch(
        "starknet_py.net.account.account_client.AccountClient.call_contract",
        MagicMock(),
    ) as mocked_call_contract:
        result = asyncio.Future()
        result.set_result([0, 0])

        mocked_call_contract.return_value = result

        await acc_client.get_balance()

        call = mocked_call_contract.call_args

    (call,) = call[0]

    assert call.to_addr == parse_address(FEE_CONTRACT_ADDRESS)


@pytest.mark.asyncio
async def test_estimate_fee_called(erc20_contract):
    with patch(
        "starknet_py.net.gateway_client.GatewayClient.estimate_fee",
        AsyncMock(),
    ) as mocked_estimate_fee:
        mocked_estimate_fee.return_value = [0]

        await erc20_contract.functions["balanceOf"].prepare("1234").estimate_fee()

        mocked_estimate_fee.assert_called()


@pytest.mark.asyncio
async def test_estimated_fee_greater_than_zero(erc20_contract, account_client):
    erc20_contract = Contract(
        erc20_contract.address, erc20_contract.data.abi, account_client
    )

    estimated_fee = (
        await erc20_contract.functions["balanceOf"]
        .prepare("1234", max_fee=10)
        .estimate_fee(block_hash="latest")
    )

    assert estimated_fee.overall_fee > 0
    assert (
        estimated_fee.gas_price * estimated_fee.gas_usage == estimated_fee.overall_fee
    )


@pytest.mark.asyncio
async def test_estimate_fee_for_declare_transaction(
    new_account_client, map_compiled_contract
):
    declare_tx = await new_account_client.sign_declare_transaction(
        compiled_contract=map_compiled_contract, max_fee=MAX_FEE
    )

    estimated_fee = await new_account_client.estimate_fee(tx=declare_tx)

    assert isinstance(estimated_fee.overall_fee, int)
    assert estimated_fee.overall_fee > 0
    assert (
        estimated_fee.gas_usage * estimated_fee.gas_price == estimated_fee.overall_fee
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("key, val", [(20, 20), (30, 30)])
async def test_sending_multicall(account_client, map_contract, key, val):
    calls = [
        map_contract.functions["put"].prepare(key=10, value=10),
        map_contract.functions["put"].prepare(key=key, value=val),
    ]

    res = await account_client.execute(calls, int(1e20))
    await account_client.wait_for_tx(res.transaction_hash)

    (value,) = await map_contract.functions["get"].call(key=key)

    assert value == val


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_block_traces(gateway_account_client):
    traces = await gateway_account_client.get_block_traces(block_number=2)

    assert traces.traces != []


@pytest.mark.asyncio
async def test_rejection_reason_in_transaction_receipt(account_client, map_contract):
    res = await map_contract.functions["put"].invoke(key=10, value=20, max_fee=1)

    with pytest.raises(TransactionRejectedError):
        await account_client.wait_for_tx(res.hash)

    transaction_receipt = await account_client.get_transaction_receipt(res.hash)

    if isinstance(account_client.client, GatewayClient):
        assert "Actual fee exceeded max fee." in transaction_receipt.rejection_reason


@pytest.mark.asyncio
async def test_sign_and_verify_offchain_message_fail(
    gateway_account_client, typed_data
):
    signature = gateway_account_client.sign_message(typed_data)
    signature = [signature[0] + 1, signature[1]]
    result = await gateway_account_client.verify_message(typed_data, signature)

    assert result is False


@pytest.mark.asyncio
async def test_sign_and_verify_offchain_message(gateway_account_client, typed_data):
    signature = gateway_account_client.sign_message(typed_data)
    result = await gateway_account_client.verify_message(typed_data, signature)

    assert result is True


@pytest.mark.asyncio
async def test_get_class_hash_at(map_contract, account_client):
    class_hash = await account_client.get_class_hash_at(
        map_contract.address, block_hash="latest"
    )

    assert class_hash != 0


@pytest.mark.asyncio
async def test_sign_transaction_unsupported_version(new_account_client):
    with pytest.raises(
        ValueError,
        match="Provided version: 0 is not equal to account's supported_tx_version: 1",
    ):
        await new_account_client.sign_invoke_transaction(
            calls=Call(0x1, 0x1, [0x1]), max_fee=MAX_FEE, version=0
        )


@pytest.mark.asyncio
async def test_sign_warns_on_max_fee_0(account_client):
    with pytest.warns(
        DeprecationWarning,
        match="Transaction will fail with max_fee set to 0. Change it to a higher value.",
    ):
        tx = await account_client.sign_invoke_transaction(
            calls=Call(0x1, 0x1, [0x1]), max_fee=0
        )
        await account_client.send_transaction(tx)
