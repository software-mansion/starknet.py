import pytest

from starknet_py.contract import Contract, ContractFunction
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_DIR

mock_contracts_base_path = CONTRACTS_DIR
base_source_code = (CONTRACTS_DIR / "base.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_deploy_tx(gateway_account_client, map_source_code):
    result = await Contract.deploy(
        client=gateway_account_client, compilation_source=map_source_code
    )
    result = await result.wait_for_acceptance()
    result = result.deployed_contract

    assert isinstance(result.functions["get"], ContractFunction)
    assert isinstance(result.functions["put"], ContractFunction)


@pytest.mark.asyncio
async def test_deploy_with_search_path(gateway_account_client):
    result = await Contract.deploy(
        client=gateway_account_client,
        compilation_source=base_source_code,
        search_paths=[str(mock_contracts_base_path)],
    )
    await result.wait_for_acceptance()

    result = await Contract.deploy(
        client=gateway_account_client,
        compilation_source=base_source_code,
        search_paths=[str(mock_contracts_base_path)],
    )
    result = await result.wait_for_acceptance()
    result = result.deployed_contract
    assert isinstance(result.functions["put"], ContractFunction)


constructor_with_arguments_source = (
    CONTRACTS_DIR / "constructor_with_arguments.cairo"
).read_text("utf-8")


@pytest.mark.asyncio
async def test_constructor_arguments():
    value = 10
    tuple_value = (1, (2, 3))
    arr = [1, 2, 3]
    struct = {"value": 12, "nested_struct": {"value": 99}}

    # Contract should throw if constructor arguments were not provided
    with pytest.raises(ValueError) as err:
        Contract.compute_address(
            compilation_source=constructor_with_arguments_source,
            salt=1234,
        )

    assert "no args were provided" in str(err.value)

    # Positional params
    address1 = Contract.compute_address(
        compilation_source=constructor_with_arguments_source,
        constructor_args=[value, tuple_value, arr, struct],
        salt=1234,
    )
    assert address1

    # Named params
    address2 = Contract.compute_address(
        compilation_source=constructor_with_arguments_source,
        constructor_args={
            "single_value": value,
            "tuple": tuple_value,
            "arr": arr,
            "dict": struct,
        },
        salt=1234,
    )
    assert address2


constructor_without_arguments_source = (
    CONTRACTS_DIR / "constructor_without_arguments.cairo"
).read_text("utf-8")


@pytest.mark.asyncio
async def test_constructor_without_arguments():
    assert Contract.compute_address(
        compilation_source=constructor_without_arguments_source,
        salt=1234,
    )
