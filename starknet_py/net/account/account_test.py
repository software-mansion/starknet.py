import pytest

from starknet_py.contract import Contract
from starknet_py.net.client_models import Call
from starknet_py.tests.e2e.utils import MAX_FEE


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


@pytest.mark.asyncio
async def test_sign_and_verify_offchain_message_fail(gateway_account, typed_data):
    signature = gateway_account.sign_message(typed_data)
    signature = [signature[0] + 1, signature[1]]
    result = await gateway_account.verify_message(typed_data, signature)

    assert result is False


@pytest.mark.asyncio
async def test_sign_and_verify_offchain_message(gateway_account, typed_data):
    signature = gateway_account.sign_message(typed_data)
    result = await gateway_account.verify_message(typed_data, signature)

    assert result is True


def test_contract_raises_on_no_client_and_account():
    with pytest.raises(ValueError) as exinfo:
        Contract(address=1234, abi=[])

    assert "One of client or account must be provided" in str(exinfo.value)


def test_contract_raises_on_both_client_and_account(gateway_client, gateway_account):
    with pytest.raises(ValueError) as exinfo:
        Contract(address=1234, abi=[], client=gateway_client, account=gateway_account)

    assert "Account and client are mutually exclusive" in str(exinfo.value)
