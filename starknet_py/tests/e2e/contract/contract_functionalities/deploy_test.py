import dataclasses
import json
import re

import pytest

from starknet_py.common import create_sierra_compiled_contract
from starknet_py.contract import Contract, DeclareResult
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR, MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.mark.asyncio
async def test_declare_deploy(
    gateway_account,
    v1_minimal_contract_class_hash: int,
):
    compiled_contract = read_contract(
        "minimal_contract_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )

    declare_result = DeclareResult(
        _account=gateway_account,
        _client=gateway_account.client,
        _cairo_version=1,
        class_hash=v1_minimal_contract_class_hash,
        compiled_contract=compiled_contract,
        hash=0,
    )

    deploy_result = await declare_result.deploy(max_fee=MAX_FEE)
    await deploy_result.wait_for_acceptance()

    assert isinstance(deploy_result.hash, int)
    assert deploy_result.hash != 0
    assert deploy_result.deployed_contract.address != 0


@pytest.mark.asyncio
async def test_throws_on_wrong_abi(
    gateway_account, v1_minimal_contract_class_hash: int
):
    compiled_contract = read_contract(
        "minimal_contract_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )

    declare_result = DeclareResult(
        _account=gateway_account,
        _client=gateway_account.client,
        _cairo_version=1,
        class_hash=v1_minimal_contract_class_hash,
        compiled_contract=compiled_contract,
        hash=0,
    )

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
async def test_deploy_contract_flow(gateway_account, v1_hello_starknet_class_hash: int):
    compiled_contract = read_contract(
        "hello_starknet_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    abi = create_sierra_compiled_contract(compiled_contract=compiled_contract).abi

    deploy_result = await Contract.deploy_contract(
        class_hash=v1_hello_starknet_class_hash,
        account=gateway_account,
        abi=json.loads(abi),
        max_fee=MAX_FEE,
        cairo_version=1,
    )
    await deploy_result.wait_for_acceptance()

    contract = deploy_result.deployed_contract

    assert isinstance(contract.address, int)
    assert len(contract.functions) != 0
