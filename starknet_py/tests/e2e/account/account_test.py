import pytest

from starknet_py.contract import Contract
from starknet_py.net.client_models import Call
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE
from starknet_py.transaction_exceptions import TransactionRejectedError


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
async def test_get_balance_throws_when_token_not_specified(account):
    with pytest.raises(ValueError) as err:
        await account.get_balance()

    assert "Token_address must be specified when using a custom net address" in str(
        err.value
    )


@pytest.mark.asyncio
async def test_balance_when_token_specified(account, erc20_contract):
    balance = await account.get_balance(erc20_contract.address)

    assert balance == 200


@pytest.mark.asyncio
async def test_estimated_fee_greater_than_zero(erc20_contract, account):
    erc20_contract = Contract(
        address=erc20_contract.address, abi=erc20_contract.data.abi, account=account
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


@pytest.mark.asyncio
async def test_estimate_fee_for_declare_transaction(account, map_compiled_contract):
    declare_tx = await account.sign_declare_transaction(
        compiled_contract=map_compiled_contract, max_fee=MAX_FEE
    )

    estimated_fee = await account.client.estimate_fee(tx=declare_tx)

    assert isinstance(estimated_fee.overall_fee, int)
    assert estimated_fee.overall_fee > 0
    assert (
        estimated_fee.gas_usage * estimated_fee.gas_price == estimated_fee.overall_fee
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("key, val", [(20, 20), (30, 30)])
async def test_sending_multicall(account, map_contract, key, val):
    calls = [
        map_contract.functions["put"].prepare(key=10, value=10),
        map_contract.functions["put"].prepare(key=key, value=val),
    ]

    res = await account.execute(calls=calls, max_fee=int(1e20))
    await account.client.wait_for_tx(res.transaction_hash)

    (value,) = await map_contract.functions["get"].call(key=key)

    assert value == val


@pytest.mark.run_on_devnet
@pytest.mark.asyncio
async def test_get_block_traces(gateway_account):
    traces = await gateway_account.client.get_block_traces(block_number=2)

    assert traces.traces != []


@pytest.mark.asyncio
async def test_rejection_reason_in_transaction_receipt(account, map_contract):
    res = await map_contract.functions["put"].invoke(key=10, value=20, max_fee=1)

    with pytest.raises(TransactionRejectedError):
        await account.client.wait_for_tx(res.hash)

    transaction_receipt = await account.client.get_transaction_receipt(res.hash)

    if isinstance(account.client, GatewayClient):
        assert "Actual fee exceeded max fee." in transaction_receipt.rejection_reason


@pytest.mark.asyncio
async def test_sign_and_verify_offchain_message_fail(account, typed_data):
    signature = account.sign_message(typed_data)
    signature = [signature[0] + 1, signature[1]]
    result = await account.verify_message(typed_data, signature)

    assert result is False


@pytest.mark.asyncio
async def test_sign_and_verify_offchain_message(account, typed_data):
    signature = account.sign_message(typed_data)
    result = await account.verify_message(typed_data, signature)

    assert result is True


@pytest.mark.asyncio
async def test_get_class_hash_at(map_contract, account):
    class_hash = await account.client.get_class_hash_at(
        map_contract.address, block_hash="latest"
    )

    assert class_hash != 0


@pytest.mark.asyncio()
async def test_get_nonce(gateway_account):
    nonce = await gateway_account.get_nonce()

    assert nonce >= 0  # TODO maybe better test


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "calls", [[Call(10, 20, [30])], [Call(10, 20, [30]), Call(40, 50, [60])]]
)
async def test_sign_invoke_transaction(gateway_account, calls):
    signed_tx = await gateway_account.sign_invoke_transaction(calls, max_fee=MAX_FEE)

    assert isinstance(signed_tx.signature, list)
    assert len(signed_tx.signature) > 0
    assert signed_tx.max_fee == MAX_FEE


@pytest.mark.asyncio
async def test_sign_declare_transaction(gateway_account, map_compiled_contract):
    signed_tx = await gateway_account.sign_declare_transaction(
        map_compiled_contract, max_fee=MAX_FEE
    )

    assert isinstance(signed_tx.signature, list)
    assert len(signed_tx.signature) > 0
    assert signed_tx.max_fee == MAX_FEE


@pytest.mark.asyncio
async def test_sign_deploy_account_transaction(gateway_account):
    class_hash = 0x1234
    salt = 0x123
    calldata = [1, 2, 3]
    signed_tx = await gateway_account.sign_deploy_account_transaction(
        class_hash, salt, calldata, max_fee=MAX_FEE
    )

    assert isinstance(signed_tx.signature, list)
    assert len(signed_tx.signature) > 0
    assert signed_tx.max_fee == MAX_FEE
    assert signed_tx.class_hash == class_hash
    assert signed_tx.contract_address_salt == salt
    assert signed_tx.constructor_calldata == calldata
