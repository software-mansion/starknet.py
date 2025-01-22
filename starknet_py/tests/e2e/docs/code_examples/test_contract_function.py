# pylint: disable=unused-variable
import pytest

from starknet_py.contract import Contract, ContractFunction
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping


def test_prepare_invoke_v1(map_contract: Contract):
    # docs-start: prepare_invoke_v1
    prepared_function_call = map_contract.functions["put"].prepare_invoke_v1(
        key=10, value=20
    )
    # docs-end: prepare_invoke_v1


def test_prepare_invoke_v3(map_contract: Contract):
    # docs-start: prepare_invoke_v3
    prepared_function_call = map_contract.functions["put"].prepare_invoke_v3(
        key=10, value=20
    )
    # docs-end: prepare_invoke_v3


@pytest.mark.asyncio
async def test_call(map_contract: Contract):
    # docs-start: call
    call_result = map_contract.functions["get"].call(key=10)
    # or when call has to be done at specific block
    call_result = map_contract.functions["get"].call(key=10, block_number="latest")
    # docs-end: call


def test_invoke_v1(map_contract: Contract):
    # docs-start: invoke_v1
    invoke_result = map_contract.functions["put"].invoke_v1(
        key=10, value=20, max_fee=int(1e15)
    )
    # docs-end: invoke_v1


def test_invoke_v3(map_contract: Contract):
    # docs-start: invoke_v3
    invoke_result = map_contract.functions["put"].invoke_v3(
        key=10,
        value=20,
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l1_data_gas=ResourceBounds(
                max_amount=int(1e5), max_price_per_unit=int(1e13)
            ),
        ),
    )
    # docs-end: invoke_v3


def test_get_selector():
    # docs-start: get_selector
    selector = ContractFunction.get_selector("get")
    # docs-end: get_selector
