import pytest

from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import EstimatedFee
from starknet_py.net.models import StarknetChainId
from starknet_py.tests.e2e.fixtures.constants import (
    MAP_CONTRACT_ADDRESS_INTEGRATION,
    MAX_FEE,
)


@pytest.mark.skip
@pytest.mark.asyncio
async def test_sign_invoke_tx_for_fee_estimation(full_node_account_integration):
    account = full_node_account_integration

    map_contract = await Contract.from_address(
        address=MAP_CONTRACT_ADDRESS_INTEGRATION, provider=account
    )

    call = map_contract.functions["put"].prepare(key=40, value=50)
    transaction = await account.sign_invoke_transaction(calls=call, max_fee=MAX_FEE)

    estimate_fee_transaction = await account.sign_for_fee_estimate(transaction)

    estimation = await account.client.estimate_fee(estimate_fee_transaction)
    assert estimation.overall_fee > 0

    # Verify that the transaction signed for fee estimation cannot be sent
    with pytest.raises(ClientError):
        await account.client.send_transaction(estimate_fee_transaction)

    # Verify that original transaction can be sent
    result = await account.client.send_transaction(transaction)
    await account.client.wait_for_tx(result.transaction_hash)


@pytest.mark.skip
@pytest.mark.asyncio
async def test_sign_declare_tx_for_fee_estimation(
    full_node_account_integration, map_compiled_contract
):
    account = full_node_account_integration

    transaction = await account.sign_declare_transaction(
        compiled_contract=map_compiled_contract, max_fee=MAX_FEE
    )

    estimate_fee_transaction = await account.sign_for_fee_estimate(transaction)

    estimation = await account.client.estimate_fee(estimate_fee_transaction)
    assert estimation.overall_fee > 0

    # Verify that the transaction signed for fee estimation cannot be sent
    with pytest.raises(ClientError):
        await account.client.declare(estimate_fee_transaction)

    # Verify that original transaction can be sent
    result = await account.client.declare(transaction)
    await account.client.wait_for_tx(result.transaction_hash)


@pytest.mark.skip
@pytest.mark.asyncio
async def test_sign_deploy_account_tx_for_fee_estimation(
    full_node_client_integration, deploy_account_details_factory
):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()

    account = Account(
        address=address,
        client=full_node_client_integration,
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
    )

    transaction = await account.sign_deploy_account_transaction(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=[key_pair.public_key],
        max_fee=MAX_FEE,
    )

    estimate_fee_transaction = await account.sign_for_fee_estimate(transaction)

    estimation = await account.client.estimate_fee(transaction)
    assert isinstance(estimation, EstimatedFee)
    assert estimation.overall_fee > 0

    # Verify that the transaction signed for fee estimation cannot be sent
    with pytest.raises(ClientError):
        await account.client.deploy_account(estimate_fee_transaction)

    # Verify that original transaction can be sent
    result = await account.client.deploy_account(transaction)
    await account.client.wait_for_tx(result.transaction_hash)
