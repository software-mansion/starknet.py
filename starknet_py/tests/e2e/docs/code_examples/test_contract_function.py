# pylint: disable=unused-variable
import pytest

from starknet_py.contract import Contract, ContractFunction


def test_prepare(base_account_deploy_map_contract: Contract):
    map_contract = base_account_deploy_map_contract
    # docs-start: prepare
    prepared_function_call = map_contract.functions["put"].prepare(key=10, value=20)
    # docs-end: prepare


@pytest.mark.asyncio
async def test_call(base_account_deploy_map_contract: Contract):
    map_contract = base_account_deploy_map_contract
    # docs-start: call
    call_result = map_contract.functions["get"].call(key=10)
    # or when call has to be done at specific block
    call_result = map_contract.functions["get"].call(key=10, block_hash="latest")
    # docs-end: call


def test_invoke(base_account_deploy_map_contract: Contract):
    map_contract = base_account_deploy_map_contract
    # docs-start: invoke
    invoke_result = map_contract.functions["put"].invoke(
        key=10, value=20, max_fee=int(1e15)
    )
    # docs-end: invoke


def test_get_selector(base_account_deploy_map_contract: Contract):
    map_contract = base_account_deploy_map_contract
    # docs-start: get_selector
    selector = ContractFunction.get_selector("get")
    # docs-end: get_selector
