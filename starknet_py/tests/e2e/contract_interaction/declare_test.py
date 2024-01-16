import pytest

from starknet_py.contract import Contract
from starknet_py.net.models import DeclareV2, DeclareV3
from starknet_py.tests.e2e.fixtures.constants import (
    CONTRACTS_COMPILED_V1_DIR,
    CONTRACTS_COMPILED_V2_DIR,
    MAX_FEE,
    MAX_RESOURCE_BOUNDS_L1,
)
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.asyncio
async def test_contract_declare_v2(account):
    compiled_contract = read_contract(
        "test_contract_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    compiled_contract_casm = read_contract(
        "test_contract_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
    )

    declare_result = await Contract.declare(
        account,
        compiled_contract=compiled_contract,
        compiled_contract_casm=compiled_contract_casm,
        max_fee=MAX_FEE,
    )
    await declare_result.wait_for_acceptance()

    assert isinstance(declare_result.declare_transaction, DeclareV2)
    assert isinstance(declare_result.hash, int)
    assert isinstance(declare_result.class_hash, int)
    assert declare_result.compiled_contract == compiled_contract


@pytest.mark.asyncio
async def test_contract_declare_v3(account):
    compiled_contract = read_contract(
        "test_contract_compiled.json", directory=CONTRACTS_COMPILED_V2_DIR
    )
    compiled_contract_casm = read_contract(
        "test_contract_compiled.casm", directory=CONTRACTS_COMPILED_V2_DIR
    )

    declare_result = await Contract.declare(
        account,
        compiled_contract=compiled_contract,
        compiled_contract_casm=compiled_contract_casm,
        tx_version=3,
        l1_resource_bounds=MAX_RESOURCE_BOUNDS_L1,
    )
    await declare_result.wait_for_acceptance()

    assert isinstance(declare_result.declare_transaction, DeclareV3)
    assert isinstance(declare_result.hash, int)
    assert isinstance(declare_result.class_hash, int)
    assert declare_result.compiled_contract == compiled_contract


@pytest.mark.asyncio
async def test_throws_when_cairo1_without_compiled_contract_casm_and_casm_class_hash(
    account,
):
    compiled_contract = read_contract("erc20_compiled.json")

    with pytest.raises(
        ValueError,
        match="Cairo 1.0 contract was provided without casm_class_hash or compiled_contract_casm argument.",
    ):
        await Contract.declare(
            account, compiled_contract=compiled_contract, max_fee=MAX_FEE
        )


@pytest.mark.asyncio
async def test_throws_when_max_fee_and_resource_bounds(
    account,
):
    compiled_contract = read_contract("erc20_compiled.json")

    with pytest.raises(
        ValueError,
        match="Arguments 'max_fee' and 'l1_resource_bounds' are mutually exclusive.",
    ):
        await Contract.declare(
            account,
            compiled_contract=compiled_contract,
            max_fee=MAX_FEE,
            l1_resource_bounds=MAX_RESOURCE_BOUNDS_L1,
        )
