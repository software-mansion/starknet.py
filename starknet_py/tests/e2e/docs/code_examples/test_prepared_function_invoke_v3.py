# pylint: disable=unused-variable
import pytest

from starknet_py.contract import Contract
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping


@pytest.mark.asyncio
async def test_invoke(map_contract: Contract):
    prepared_function_call = map_contract.functions["put"].prepare_invoke_v3(
        key=10, value=20
    )
    # docs-start: invoke
    resource_bounds = ResourceBoundsMapping(
        l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        l2_gas=ResourceBounds(max_amount=int(1e10), max_price_per_unit=int(1e20)),
        l1_data_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
    )
    invoke_result = await prepared_function_call.invoke(resource_bounds=resource_bounds)
    # docs-end: invoke
    prepared_function_call.resource_bounds = None
    # docs-start: invoke
    # resource_bounds can be estimated automatically
    invoke_result = await prepared_function_call.invoke(auto_estimate=True)
    # or if resource_bounds was specified in prepared_function_call
    # docs-end: invoke
    prepared_function_call.resource_bounds = resource_bounds
    # docs-start: invoke
    invoke_result = await prepared_function_call.invoke()
    # docs-end: invoke
