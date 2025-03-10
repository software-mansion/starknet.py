import sys

import pytest

from starknet_py.tests.e2e.fixtures.misc import load_contract


@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_simple_declare_and_deploy(account):
    # pylint: disable=import-outside-toplevel
    # docs: start
    from starknet_py.contract import Contract
    from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping

    # docs: end
    compiled_contract = load_contract("AccountCopy1")
    constructor_args = {"public_key": 0x123}

    # docs: start
    declare_result = await Contract.declare_v3(
        account=account,
        compiled_contract=compiled_contract["sierra"],
        compiled_contract_casm=compiled_contract["casm"],
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17)),
            l1_data_gas=ResourceBounds(
                max_amount=int(1e5), max_price_per_unit=int(1e13)
            ),
        ),
    )
    await declare_result.wait_for_acceptance()

    deploy_result = await declare_result.deploy_v3(
        constructor_args=constructor_args,
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17)),
            l1_data_gas=ResourceBounds(
                max_amount=int(1e5), max_price_per_unit=int(1e13)
            ),
        ),
    )
    await deploy_result.wait_for_acceptance()

    contract = deploy_result.deployed_contract
    # docs: end

    assert isinstance(declare_result.hash, int)
    assert isinstance(declare_result.class_hash, int)
    assert declare_result.compiled_contract == compiled_contract["sierra"]
    assert contract.address != 0
