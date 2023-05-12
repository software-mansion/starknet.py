import dataclasses
import json
import re
from pathlib import Path

import pytest

from starknet_py.common import create_casm_class, create_sierra_compiled_contract
from starknet_py.contract import Contract
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
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
        (
            "test_enum_compiled.json",
            "test_enum_compiled.casm",
            CONTRACTS_COMPILED_V1_DIR,
        ),
        (
            "test_option_compiled.json",
            "test_option_compiled.casm",
            CONTRACTS_COMPILED_V1_DIR,
        ),
    ],
)
async def test_declare_deploy(
    file_name: str,
    directory: Path,
    casm_file_name: str,
    gateway_account,
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

    deploy_result = await declare_result.deploy(max_fee=MAX_FEE)
    await deploy_result.wait_for_acceptance()

    assert isinstance(deploy_result.hash, int)
    assert deploy_result.hash != 0
    assert deploy_result.deployed_contract.address != 0


@pytest.mark.asyncio
async def test_throws_on_wrong_abi(gateway_account):
    compiled_contract = read_contract(
        "minimal_contract_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    compiled_contract_casm = read_contract(
        "minimal_contract_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
    )

    declare_result = await Contract.declare(
        gateway_account,
        compiled_contract=compiled_contract,
        compiled_contract_casm=compiled_contract_casm,
        max_fee=MAX_FEE,
    )
    await declare_result.wait_for_acceptance()

    compiled_contract = compiled_contract.replace('"abi": [', '"abi": ')
    declare_result = dataclasses.replace(
        declare_result, compiled_contract=compiled_contract
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Contract's ABI can't be converted to format List[Dict]. "
            "Make sure provided compiled_contract is correct."
        ),
    ):
        await declare_result.deploy(max_fee=MAX_FEE)


@pytest.mark.asyncio
async def test_deploy_contract_flow(gateway_account):
    compiled_contract = read_contract(
        "hello_starknet_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    compiled_contract_casm = read_contract(
        "hello_starknet_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
    )
    casm_class_hash = compute_casm_class_hash(create_casm_class(compiled_contract_casm))

    declare_tx = await gateway_account.sign_declare_v2_transaction(
        compiled_contract, casm_class_hash, max_fee=MAX_FEE
    )
    resp = await gateway_account.client.declare(declare_tx)
    await gateway_account.client.wait_for_tx(resp.transaction_hash)

    abi = create_sierra_compiled_contract(compiled_contract=compiled_contract).abi

    deploy_result = await Contract.deploy_contract(
        class_hash=resp.class_hash,
        account=gateway_account,
        abi=json.loads(abi),
        max_fee=MAX_FEE,
        cairo_version=1,
    )
    await deploy_result.wait_for_acceptance()

    contract = deploy_result.deployed_contract

    assert isinstance(contract.address, int)
    assert len(contract.functions) != 0
