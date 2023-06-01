import pytest

from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


@pytest.mark.asyncio
async def test_declare_tx(account, map_compiled_contract):
    declare_tx = await account.sign_declare_transaction(
        compiled_contract=map_compiled_contract, max_fee=MAX_FEE
    )
    result = await account.client.declare(declare_tx)

    await account.client.wait_for_tx(
        tx_hash=result.transaction_hash, wait_for_accept=True
    )


@pytest.mark.asyncio
async def test_declare_v2_tx_full_node_client(
    full_node_account, sierra_minimal_compiled_contract_and_class_hash
):
    (
        compiled_contract,
        compiled_class_hash,
    ) = sierra_minimal_compiled_contract_and_class_hash

    declare_tx = await full_node_account.sign_declare_v2_transaction(
        compiled_contract=compiled_contract,
        compiled_class_hash=compiled_class_hash,
        max_fee=MAX_FEE,
    )
    assert declare_tx.version == 2
    declare_result = await full_node_account.client.declare(declare_tx)
    await full_node_account.client.wait_for_tx(
        tx_hash=declare_result.transaction_hash, wait_for_accept=True
    )


@pytest.mark.asyncio
async def test_declare_v2_tx_gateway_client(
    gateway_account, another_sierra_minimal_compiled_contract_and_class_hash
):
    (
        compiled_contract,
        compiled_class_hash,
    ) = another_sierra_minimal_compiled_contract_and_class_hash

    declare_tx = await gateway_account.sign_declare_v2_transaction(
        compiled_contract=compiled_contract,
        compiled_class_hash=compiled_class_hash,
        max_fee=MAX_FEE,
    )
    assert declare_tx.version == 2
    declare_result = await gateway_account.client.declare(declare_tx)
    await gateway_account.client.wait_for_tx(
        tx_hash=declare_result.transaction_hash, wait_for_accept=True
    )
