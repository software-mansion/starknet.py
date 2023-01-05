import pytest


@pytest.mark.asyncio
async def test_declaring_contracts(account, map_compiled_contract):
    contract_compiled = map_compiled_contract

    # docs: start
    # Account.sign_declare_transaction takes contract source code or compiled contract
    # and returns Declare transaction
    declare_transaction = await account.sign_declare_transaction(
        compiled_contract=contract_compiled, max_fee=int(1e16)
    )

    # To declare a contract, send Declare transaction with Client.declare method
    resp = await account.client.declare(transaction=declare_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    declared_contract_class_hash = resp.class_hash
    # docs: end

    assert declared_contract_class_hash != 0
