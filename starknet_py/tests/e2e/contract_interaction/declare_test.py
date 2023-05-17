import pytest

from starknet_py.contract import Contract
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR, MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.asyncio
async def test_contract_declare(gateway_account):
    compiled_contract = read_contract(
        "test_contract_declare_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    compiled_contract_casm = read_contract(
        "test_contract_declare_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
    )

    declare_result = await Contract.declare(
        gateway_account,
        compiled_contract=compiled_contract,
        compiled_contract_casm=compiled_contract_casm,
        max_fee=MAX_FEE,
    )
    await declare_result.wait_for_acceptance()

    assert isinstance(declare_result.hash, int)
    assert isinstance(declare_result.class_hash, int)
    assert declare_result.compiled_contract == compiled_contract


@pytest.mark.asyncio
async def test_throws_when_cairo1_without_compiled_contract_casm(gateway_account):
    compiled_contract = read_contract(
        "erc20_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )

    with pytest.raises(
        ValueError,
        match="Cairo 1.0 contract was provided without compiled_contract_casm argument.",
    ):
        await Contract.declare(
            gateway_account, compiled_contract=compiled_contract, max_fee=MAX_FEE
        )
