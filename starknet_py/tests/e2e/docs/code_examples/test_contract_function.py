# pylint: disable=unused-variable
import pytest

from starknet_py.contract import Contract, ContractFunction


def test_prepare(map_contract: Contract):
    # docs-start: prepare
    prepared_function_call = map_contract.functions["put"].prepare(key=10, value=20)
    # docs-end: prepare


@pytest.mark.asyncio
async def test_call(map_contract: Contract):
    # docs-start: call
    call_result = map_contract.functions["get"].call(key=10)
    # or when call has to be done at specific block
    call_result = map_contract.functions["get"].call(key=10, block_hash="latest")
    # docs-end: call


def test_invoke(map_contract: Contract):
    # docs-start: invoke
    invoke_result = map_contract.functions["put"].invoke(
        key=10, value=20, max_fee=int(1e15)
    )
    # docs-end: invoke


def test_get_selector():
    # docs-start: get_selector
    selector = ContractFunction.get_selector("get")
    # docs-end: get_selector
