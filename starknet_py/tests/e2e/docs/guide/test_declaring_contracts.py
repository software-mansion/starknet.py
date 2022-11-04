import pytest


@pytest.mark.asyncio
async def test_declaring_contracts(new_gateway_account_client, map_source_code):
    account_client = new_gateway_account_client
    contract_source_code = map_source_code

    # docs: start
    # AccountClient.sign_declare_transaction takes contract source code or compiled contract
    # and returns Declare transaction
    declare_transaction = await account_client.sign_declare_transaction(
        compilation_source=contract_source_code, max_fee=int(1e16)
    )

    # To declare a contract, send Declare transaction with AccountClient.declare method
    resp = await account_client.declare(transaction=declare_transaction)
    await account_client.wait_for_tx(resp.transaction_hash)

    declared_contract_class_hash = resp.class_hash
    # docs: end

    assert declared_contract_class_hash != 0
