# pylint: disable=unused-variable
import pytest


@pytest.mark.asyncio
async def test_call_raw(base_account_deploy_map_contract):
    map_contract = base_account_deploy_map_contract
    prepared_function_call = map_contract.functions["get"].prepare(key=10)
    # docs-start: call_raw
    raw_response = await prepared_function_call.call_raw(block_hash="latest")
    # docs-end: call_raw


@pytest.mark.asyncio
async def test_call(base_account_deploy_map_contract):
    map_contract = base_account_deploy_map_contract
    prepared_function_call = map_contract.functions["get"].prepare(key=10)
    # docs-start: call
    response = await prepared_function_call.call_raw(block_hash="latest")
    # docs-end: call


@pytest.mark.asyncio
async def test_invoke(base_account_deploy_map_contract):
    map_contract = base_account_deploy_map_contract
    prepared_function_call = map_contract.functions["put"].prepare(key=10, value=20)
    # docs-start: invoke
    invoke_result = await prepared_function_call.invoke(max_fee=int(1e15))
    # docs-end: invoke
    prepared_function_call.max_fee = None
    # docs-start: invoke
    invoke_result = await prepared_function_call.invoke(auto_estimate=True)
    # or if max_fee was specified in prepared_function_call
    # docs-end: invoke
    prepared_function_call.max_fee = int(1e15)
    # docs-start: invoke
    invoke_result = await prepared_function_call.invoke()
    # docs-end: invoke
