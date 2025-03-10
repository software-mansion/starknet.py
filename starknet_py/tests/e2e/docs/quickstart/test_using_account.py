import os
import sys

import pytest

from starknet_py.net.client_models import ResourceBoundsMapping

directory = os.path.dirname(__file__)


@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_using_account(account, map_compiled_contract_and_class_hash_copy_2):
    # pylint: disable=import-outside-toplevel, duplicate-code, too-many-locals
    (compiled_contract, class_hash) = map_compiled_contract_and_class_hash_copy_2
    # docs: start
    from starknet_py.contract import Contract
    from starknet_py.net.client_models import ResourceBounds

    # docs: end
    # docs: start
    l1_resource_bounds = ResourceBounds(
        max_amount=int(1e5), max_price_per_unit=int(1e13)
    )
    resource_bounds = ResourceBoundsMapping(
        l1_gas=l1_resource_bounds,
        l2_gas=ResourceBounds.init_with_zeros(),
        l1_data_gas=ResourceBounds.init_with_zeros(),
    )
    # Declare and deploy an example contract which implements a simple k-v store.
    # Contract.declare_v3 takes string containing a compiled contract (sierra) and
    # a class hash (casm_class_hash) or string containing a compiled contract (casm)
    declare_result = await Contract.declare_v3(
        account,
        compiled_contract=compiled_contract,
        compiled_class_hash=class_hash,
        resource_bounds=resource_bounds,
    )

    await declare_result.wait_for_acceptance()
    deploy_result = await declare_result.deploy_v3(
        resource_bounds=resource_bounds,
    )
    # Wait until deployment transaction is accepted
    await deploy_result.wait_for_acceptance()

    # Get deployed contract
    map_contract = deploy_result.deployed_contract
    k, v = 13, 4324
    # Adds a transaction to mutate the state of k-v store. The call goes through account proxy, because we've used
    # Account to create the contract object
    resource_bounds = ResourceBoundsMapping(
        l1_gas=l1_resource_bounds,
        l2_gas=ResourceBounds.init_with_zeros(),
        l1_data_gas=ResourceBounds.init_with_zeros(),
    )
    await (
        await map_contract.functions["put"].invoke_v3(
            k,
            v,
            resource_bounds=resource_bounds,
        )
    ).wait_for_acceptance()

    # Retrieves the value, which is equal to 4324 in this case
    (resp,) = await map_contract.functions["get"].call(k)

    # There is a possibility of invoking the multicall

    # Creates a list of prepared function calls
    calls = [
        map_contract.functions["put"].prepare_invoke_v3(key=10, value=20),
        map_contract.functions["put"].prepare_invoke_v3(key=30, value=40),
    ]

    # Executes only one transaction with prepared calls
    transaction_response = await account.execute_v3(
        calls=calls,
        resource_bounds=resource_bounds,
    )
    await account.client.wait_for_tx(transaction_response.transaction_hash)
    # docs: end

    assert resp == v
