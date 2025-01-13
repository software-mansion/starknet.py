import sys

import pytest

from starknet_py.net.client_models import ResourceBounds


@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_declaring_contracts(
    account, map_compiled_contract_and_class_hash_copy_1
):
    (compiled_contract, class_hash) = map_compiled_contract_and_class_hash_copy_1

    # docs: start
    # Account.sign_declare_v3 takes a string containing a compiled contract (sierra)
    # and a class hash (casm_class_hash)

    declare_transaction = await account.sign_declare_v3(
        compiled_contract=compiled_contract,
        compiled_class_hash=class_hash,
        l1_resource_bounds=ResourceBounds(
            max_amount=int(1e5), max_price_per_unit=int(1e13)
        ),
    )

    # To declare a contract, send Declare transaction with Client.declare method
    resp = await account.client.declare(transaction=declare_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    declared_contract_class_hash = resp.class_hash
    # docs: end

    assert declared_contract_class_hash != 0
