import pytest


@pytest.mark.asyncio
async def test_declare_v2(account, sierra_minimal_compiled_contract_and_class_hash):
    (
        contract_compiled,
        compiled_class_hash,
    ) = sierra_minimal_compiled_contract_and_class_hash

    # pylint: disable=import-outside-toplevel
    # docs: start
    from starknet_py.hash.casm_class_hash import compute_casm_class_hash
    from starknet_py.net.schemas.gateway import CasmClassSchema

    # contract_compiled is the output of the starknet-sierra-compile (.casm file)
    casm_class = CasmClassSchema().loads(contract_compiled)

    # Compute Casm class hash
    casm_class_hash = compute_casm_class_hash(casm_class)
    # docs: end
    assert casm_class_hash == compiled_class_hash
    # docs: start

    # Create Declare v2 transaction
    declare_v2_transaction = await account.sign_declare_v2_transaction(
        compiled_contract=contract_compiled,
        compiled_class_hash=casm_class_hash,
        max_fee=int(1e16),
    )

    # Send Declare v2 transaction
    resp = await account.client.declare(transaction=declare_v2_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    declared_contract_class_hash = resp.class_hash
    # docs: end

    assert declared_contract_class_hash != 0
