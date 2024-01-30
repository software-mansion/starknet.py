import pytest

from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.asyncio
async def test_simple_declare_and_deploy(account):
    # pylint: disable=import-outside-toplevel
    # docs: start
    from starknet_py.contract import Contract

    # docs: end
    compiled_contract = read_contract("account_compiled.json")
    compiled_contract_casm = read_contract("account_compiled.casm")
    constructor_args = {"public_key_": 0x123}

    # docs: start
    declare_result = await Contract.declare_v2(
        account=account,
        compiled_contract=compiled_contract,
        compiled_contract_casm=compiled_contract_casm,
        max_fee=int(1e16),
    )
    await declare_result.wait_for_acceptance()

    deploy_result = await declare_result.deploy_v1(
        constructor_args=constructor_args, max_fee=int(1e16)
    )
    await deploy_result.wait_for_acceptance()

    contract = deploy_result.deployed_contract
    # docs: end

    assert isinstance(declare_result.hash, int)
    assert isinstance(declare_result.class_hash, int)
    assert declare_result.compiled_contract == compiled_contract
    assert contract.address != 0
    assert len(contract.functions) > 0
