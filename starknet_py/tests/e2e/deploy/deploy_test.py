import os
from pathlib import Path
import pytest

from starknet_py.contract import Contract, ContractFunction
from starknet_py.tests.e2e.utils import DevnetClientFactory

directory = os.path.dirname(__file__)
map_source_code = Path(directory, "map.cairo").read_text("utf-8")

mock_contracts_base_path = Path(directory, "mock-contracts")
base_source_code = Path(os.path.join(mock_contracts_base_path, "base.cairo")).read_text(
    "utf-8"
)


@pytest.mark.asyncio
async def test_deploy_tx(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()
    result = await Contract.deploy(client=client, compilation_source=map_source_code)
    await result.wait_for_acceptance()

    result = await Contract.deploy(client=client, compilation_source=map_source_code)
    result = await result.wait_for_acceptance()
    result = result.deployed_contract
    assert isinstance(result.functions["get"], ContractFunction)
    assert isinstance(result.functions["put"], ContractFunction)


@pytest.mark.asyncio
async def test_deploy_with_search_path(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()
    result = await Contract.deploy(
        client=client,
        compilation_source=base_source_code,
        search_paths=[str(mock_contracts_base_path)],
    )
    await result.wait_for_acceptance()

    result = await Contract.deploy(
        client=client,
        compilation_source=base_source_code,
        search_paths=[str(mock_contracts_base_path)],
    )
    result = await result.wait_for_acceptance()
    result = result.deployed_contract
    assert isinstance(result.functions["put"], ContractFunction)


constructor_with_arguments_source = Path(
    directory, "constructor_with_arguments.cairo"
).read_text("utf-8")


@pytest.mark.asyncio
async def test_constructor_arguments(run_devnet):
    value = 10
    tuple_value = (1, (2, 3))
    arr = [1, 2, 3]
    struct = {"value": 12, "nested_struct": {"value": 99}}
    client = await DevnetClientFactory(run_devnet).make_devnet_client()

    # Contract should throw if constructor arguments were not provided
    with pytest.raises(ValueError) as err:
        await Contract.deploy(
            client=client, compilation_source=constructor_with_arguments_source
        )

    assert "no args were provided" in str(err.value)

    # Positional params
    contract_1 = await Contract.deploy(
        client=client,
        compilation_source=constructor_with_arguments_source,
        constructor_args=[value, tuple_value, arr, struct],
    )
    contract_1 = await contract_1.wait_for_acceptance()
    contract_1 = contract_1.deployed_contract

    # Named params
    contract_2 = await Contract.deploy(
        client=client,
        compilation_source=constructor_with_arguments_source,
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


constructor_without_arguments_source = Path(
    directory, "constructor_without_arguments.cairo"
).read_text("utf-8")


@pytest.mark.asyncio
async def test_constructor_without_arguments(run_devnet):
    client = await DevnetClientFactory(run_devnet).make_devnet_client()

    result = await Contract.deploy(
        client=client, compilation_source=constructor_without_arguments_source
    )
    result = await result.wait_for_acceptance()
    contract = result.deployed_contract

    assert contract.address is not None
