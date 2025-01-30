import pytest

from starknet_py.net.models import InvokeV3


@pytest.mark.asyncio
async def test_create_invoke_from_contract(map_contract, account):
    # pylint: disable=import-outside-toplevel
    contract = map_contract

    # docs: start
    from starknet_py.net.client_models import (
        Call,
        ResourceBounds,
        ResourceBoundsMapping,
    )

    # Prepare a call through Contract
    call = contract.functions["put"].prepare_invoke_v3(key=20, value=30)
    assert issubclass(type(call), Call)

    # Crate an Invoke transaction from call
    invoke_transaction = await account.sign_invoke_v3(
        call,
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l1_data_gas=ResourceBounds(
                max_amount=int(1e5), max_price_per_unit=int(1e13)
            ),
            l2_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        ),
    )
    # docs: end

    assert isinstance(invoke_transaction, InvokeV3)
