import os
from pathlib import Path
import pytest

from starknet.contract import Contract, ContractFunction
from starknet.tests.e2e.utils import DevnetClient

directory = os.path.dirname(__file__)
map_source_code = Path(directory, "map.cairo").read_text("utf-8")


@pytest.mark.asyncio
async def test_deploy_tx():
    client = DevnetClient()
    result = await Contract.deploy(client=client, compilation_source=map_source_code)
    assert isinstance(result.functions["get"], ContractFunction)
    assert isinstance(result.functions["put"], ContractFunction)


constructor_with_arguments_source = Path(
    directory, "constructor_with_arguments.cairo"
).read_text("utf-8")


@pytest.mark.asyncio
async def test_constructor_arguments():
    value = 10
    tuple_value = (1, (2, 3))
    arr = [1, 2, 3]
    struct = {"value": 12, "nested_struct": {"value": 99}}
    client = DevnetClient()

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

    assert contract_1.address != contract_2.address

    result_1 = await contract_1.functions["get"].call()
    result_2 = await contract_1.functions["get"].call()

    assert result_1 == (value, tuple_value, sum(arr), struct)
    assert result_2 == (value, tuple_value, sum(arr), struct)


constructor_without_arguments_source = Path(
    directory, "constructor_without_arguments.cairo"
).read_text("utf-8")


@pytest.mark.asyncio
async def test_constructor_without_arguments():
    client = DevnetClient()

    contract = await Contract.deploy(
        client=client, compilation_source=constructor_without_arguments_source
    )

    assert contract.address is not None
