from pathlib import Path

import pytest

from starknet_py.contract import Contract
from starknet_py.tests.e2e.fixtures.constants import (
    CONTRACTS_COMPILED_DIR,
    CONTRACTS_COMPILED_V1_DIR,
    MAX_FEE,
)
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "file_name, casm_file_name, directory",
    [
        ("erc20_compiled.json", None, CONTRACTS_COMPILED_DIR),
        ("balance_compiled.json", None, CONTRACTS_COMPILED_DIR),
        ("erc20_compiled.json", "erc20_compiled.casm", CONTRACTS_COMPILED_V1_DIR),
        (
            "token_bridge_compiled.json",
            "token_bridge_compiled.casm",
            CONTRACTS_COMPILED_V1_DIR,
        ),
    ],
)
async def test_declare(
    file_name: str, directory: Path, casm_file_name: str, gateway_account
):
    # pylint: disable=protected-access
    compiled_contract = read_contract(file_name, directory=directory)
    compiled_contract_casm = (
        read_contract(casm_file_name, directory=directory)
        if casm_file_name is not None
        else None
    )

    declare_result = await Contract.declare(
        gateway_account,
        compiled_contract=compiled_contract,
        compiled_contract_casm=compiled_contract_casm,
        max_fee=MAX_FEE,
    )
    await declare_result.wait_for_acceptance()

    assert isinstance(declare_result.hash, int)
    assert declare_result.hash != 0
    assert (
        declare_result._cairo_version == 0
        if casm_file_name is None
        else declare_result._cairo_version == 1
    )


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
