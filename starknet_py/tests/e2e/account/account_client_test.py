import asyncio
from unittest.mock import patch, MagicMock

import pytest

from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.account.account_client import deploy_account_contract
from starknet_py.net.models.transaction_payloads import TransactionStatus
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import parse_address, StarknetChainId
from starknet_py.net.networks import TESTNET, MAINNET
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.transaction_exceptions import TransactionRejectedError
from starknet_py.transactions.deploy import make_deploy_tx

MAX_FEE = int(1e20)


@pytest.mark.asyncio
async def test_deploy_account_contract_and_sign_tx(map_contract):
    k, v = 13, 4324
    await (
        await map_contract.functions["put"].invoke(k, v, max_fee=MAX_FEE)
    ).wait_for_acceptance()
    (resp,) = await map_contract.functions["get"].call(k)

    assert resp == v


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_balance_throws_when_token_not_specified(account_client):
    with pytest.raises(ValueError) as err:
        await account_client.get_balance()

    assert "Token_address must be specified when using a custom net address" in str(
        err.value
    )


@pytest.mark.asyncio
async def test_balance_when_token_specified(account_client, erc20_contract):
    balance = await account_client.get_balance(erc20_contract.address)

    assert balance == 200


@pytest.mark.asyncio
@pytest.mark.parametrize("net", (TESTNET, MAINNET))
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
        "starknet_py.net.account.account_client.AccountClient.estimate_fee", MagicMock()
    ) as mocked_estimate_fee:
        result = asyncio.Future()
        result.set_result([0])

        mocked_estimate_fee.return_value = result

        await erc20_contract.functions["balanceOf"].prepare("1234").estimate_fee()

        mocked_estimate_fee.assert_called()


@pytest.mark.asyncio
async def test_estimated_fee_greater_than_zero(erc20_contract, account_client):
    erc20_contract = Contract(
        erc20_contract.address, erc20_contract.data.abi, account_client
    )

    estimated_fee = (
        await erc20_contract.functions["balanceOf"]
        .prepare("1234", max_fee=0)
        .estimate_fee(block_hash="latest")
    )

    assert estimated_fee.overall_fee > 0
    assert (
        estimated_fee.gas_price * estimated_fee.gas_usage == estimated_fee.overall_fee
    )


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_create_account_client(network):
    client = GatewayClient(net=network)
    acc_client = await AccountClient.create_account(
        client=client, chain=StarknetChainId.TESTNET
    )
    assert acc_client.signer is not None
    assert acc_client.address is not None


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_create_account_client_with_private_key(network):
    private_key = 1234
    gt_client = GatewayClient(net=network)
    acc_client = await AccountClient.create_account(
        client=gt_client, private_key=private_key, chain=StarknetChainId.TESTNET
    )

    # Ignore typing, because BaseSigner doesn't have private_key property, but this one has
    assert acc_client.signer.private_key == private_key  # pyright: ignore
    assert acc_client.signer is not None
    assert acc_client.address is not None


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_create_account_client_with_signer(network):
    key_pair = KeyPair.from_private_key(1234)
    client = GatewayClient(
        net=network,
    )
    address = await deploy_account_contract(
        client=client,
        public_key=key_pair.public_key,
    )

    signer = StarkCurveSigner(
        account_address=address, key_pair=key_pair, chain_id=StarknetChainId.TESTNET
    )
    acc_client = await AccountClient.create_account(client=client, signer=signer)
    assert acc_client.signer == signer
    assert acc_client.signer is not None
    assert acc_client.address is not None


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
    traces = await gateway_account_client.get_block_traces(block_number=1)

    assert traces.traces != []


@pytest.mark.asyncio
async def test_deploy(account_client, map_source_code):
    deploy_tx = make_deploy_tx(compilation_source=map_source_code)
    result = await account_client.deploy(deploy_tx)
    await account_client.wait_for_tx(result.transaction_hash)

    transaction_receipt = await account_client.get_transaction_receipt(
        result.transaction_hash
    )

    assert transaction_receipt.status != TransactionStatus.NOT_RECEIVED
    assert result.contract_address


@pytest.mark.asyncio
async def test_rejection_reason_in_transaction_receipt(account_client, map_contract):
    res = await map_contract.functions["put"].invoke(key=10, value=20, max_fee=1)

    with pytest.raises(TransactionRejectedError):
        await account_client.wait_for_tx(res.hash)

    transaction_receipt = await account_client.get_transaction_receipt(res.hash)

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
async def test_throws_on_wrong_transaction_version(new_deploy_map_contract):
    with pytest.raises(ValueError) as err:
        await new_deploy_map_contract.functions["put"].invoke(
            key=10, value=20, version=0, max_fee=MAX_FEE
        )

    assert (
        "Provided version: 0 is not equal to account's supported_tx_version: 1"
        in str(err.value)
    )
