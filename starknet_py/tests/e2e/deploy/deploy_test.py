import pytest

from starknet_py.contract import Contract, ContractFunction


@pytest.mark.asyncio
async def test_deploy_tx(gateway_account_client, map_compiled_contract):
    result = await Contract.deploy(
        client=gateway_account_client, compiled_contract=map_compiled_contract
    )
    result = await result.wait_for_acceptance()
    result = result.deployed_contract

    assert isinstance(result.functions["get"], ContractFunction)
    assert isinstance(result.functions["put"], ContractFunction)


@pytest.mark.asyncio
async def test_deploy_with_search_path(gateway_account_client, base_compiled_contract):
    result = await Contract.deploy(
        client=gateway_account_client,
        compiled_contract=base_compiled_contract,
    )
    await result.wait_for_acceptance()

    result = await Contract.deploy(
        client=gateway_account_client,
        compiled_contract=base_compiled_contract,
    )
    result = await result.wait_for_acceptance()
    result = result.deployed_contract
    assert isinstance(result.functions["put"], ContractFunction)


@pytest.mark.asyncio
async def test_constructor_arguments(
    gateway_account_client, constructor_with_arguments_compiled_contract
):
    value = 10
    tuple_value = (1, (2, 3))
    arr = [1, 2, 3]
    struct = {"value": 12, "nested_struct": {"value": 99}}

    # Contract should throw if constructor arguments were not provided
    with pytest.raises(ValueError) as err:
        await Contract.deploy(
            client=gateway_account_client,
            compiled_contract=constructor_with_arguments_compiled_contract,
        )

    assert "no arguments were provided" in str(err.value)

    # Positional params
    contract_1 = await Contract.deploy(
        client=gateway_account_client,
        compiled_contract=constructor_with_arguments_compiled_contract,
        constructor_args=[value, tuple_value, arr, struct],
    )
    contract_1 = await contract_1.wait_for_acceptance()
    contract_1 = contract_1.deployed_contract

    # Named params
    contract_2 = await Contract.deploy(
        client=gateway_account_client,
        compiled_contract=constructor_with_arguments_compiled_contract,
        constructor_args={
            "single_value": value,
            "tuple": tuple_value,
            "arr": arr,
            "dict": struct,
        },
    )
    await contract_2.wait_for_acceptance()
    contract_2 = contract_2.deployed_contract

    assert contract_1.address != contract_2.address

    result_1 = await contract_1.functions["get"].call()
    result_2 = await contract_1.functions["get"].call()

    assert result_1 == (value, tuple_value, sum(arr), struct)
    assert result_2 == (value, tuple_value, sum(arr), struct)


@pytest.mark.asyncio
async def test_constructor_without_arguments(
    gateway_account_client, constructor_without_arguments_compiled_contract
):
    result = await Contract.deploy(
        client=gateway_account_client,
        compiled_contract=constructor_without_arguments_compiled_contract,
    )
    result = await result.wait_for_acceptance()
    contract = result.deployed_contract

    assert contract.address is not None
