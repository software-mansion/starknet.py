import pytest

from starknet_py.common import create_compiled_contract
from starknet_py.contract import Contract, ContractFunction
from starknet_py.net.models.typed_data import DeployerConfig
from starknet_py.tests.e2e.account.account_client_test import MAX_FEE
from starknet_py.tests.e2e.conftest import contracts_dir

mock_contracts_base_path = contracts_dir
base_source_code = (contracts_dir / "base.cairo").read_text("utf-8")


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
    contracts_dir / "constructor_with_arguments.cairo"
).read_text("utf-8")


@pytest.mark.asyncio
async def test_constructor_arguments(gateway_account_client):
    value = 10
    tuple_value = (1, (2, 3))
    arr = [1, 2, 3]
    struct = {"value": 12, "nested_struct": {"value": 99}}

    # Contract should throw if constructor arguments were not provided
    with pytest.raises(ValueError) as err:
        await Contract.deploy(
            client=gateway_account_client,
            compilation_source=constructor_with_arguments_source,
        )

    assert "no args were provided" in str(err.value)

    # Positional params
    contract_1 = await Contract.deploy(
        client=gateway_account_client,
        compilation_source=constructor_with_arguments_source,
        constructor_args=[value, tuple_value, arr, struct],
    )
    contract_1 = await contract_1.wait_for_acceptance()
    contract_1 = contract_1.deployed_contract

    # Named params
    contract_2 = await Contract.deploy(
        client=gateway_account_client,
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


constructor_without_arguments_source = (
    contracts_dir / "constructor_without_arguments.cairo"
).read_text("utf-8")


@pytest.mark.asyncio
async def test_constructor_without_arguments(gateway_account_client):
    result = await Contract.deploy(
        client=gateway_account_client,
        compilation_source=constructor_without_arguments_source,
    )
    result = await result.wait_for_acceptance()
    contract = result.deployed_contract

    assert contract.address is not None


@pytest.mark.asyncio
async def test_default_deploy_with_class_hash(
    deployer_address, account_client, map_class_hash
):
    res = await account_client.deploy_contract(
        DeployerConfig(class_hash=map_class_hash),
        deployer_address=deployer_address,
        max_fee=MAX_FEE,
    )

    assert isinstance(res, int)
    assert res != 0


@pytest.mark.asyncio
async def test_throws_when_deployer_address_not_specified_on_custom_network(
    account_client, map_class_hash
):
    with pytest.raises(ValueError) as err:
        await account_client.deploy_contract(
            DeployerConfig(class_hash=map_class_hash), max_fee=MAX_FEE
        )

    assert "deployer_address is required when not using predefined networks." in str(
        err.value
    )


@pytest.mark.asyncio
async def test_throws_when_constructor_calldata_without_abi(
    account_client, map_class_hash, deployer_address
):
    with pytest.raises(ValueError) as err:
        await account_client.deploy_contract(
            DeployerConfig(
                class_hash=map_class_hash,
                constructor_calldata=[12, 34],
            ),
            deployer_address=deployer_address,
            max_fee=MAX_FEE,
        )

    assert "constructor_calldata was provided without an abi" in str(err.value)


@pytest.mark.asyncio
async def test_throws_when_constructor_calldata_not_provided(
    account_client, deployer_address
):
    compiled_contract = create_compiled_contract(
        compilation_source=constructor_with_arguments_source
    )
    abi = compiled_contract.abi

    with pytest.raises(ValueError) as err:
        await account_client.deploy_contract(
            DeployerConfig(class_hash=1234),
            abi=abi,
            deployer_address=deployer_address,
            max_fee=MAX_FEE,
        )

    assert "Provided contract has a constructor and no arguments were provided." in str(
        err.value
    )


@pytest.mark.asyncio
async def test_constructor_arguments_deploy_contract(
    account_client, new_gateway_account_client, deployer_address
):
    # pylint: disable=too-many-locals
    abi = (
        create_compiled_contract(compilation_source=constructor_with_arguments_source)
    ).abi
    class_hash = (
        await new_gateway_account_client.declare(
            await new_gateway_account_client.sign_declare_transaction(
                compilation_source=constructor_with_arguments_source, max_fee=MAX_FEE
            )
        )
    ).class_hash

    value = 10
    tuple_value = (1, (2, 3))
    arr = [1, 2, 3]
    struct = {"value": 12, "nested_struct": {"value": 99}}

    # Contract should throw if constructor arguments were not provided
    with pytest.raises(ValueError) as err:
        await account_client.deploy_contract(
            DeployerConfig(class_hash=class_hash),
            deployer_address=deployer_address,
            abi=abi,
            max_fee=MAX_FEE,
        )

    assert "no args were provided" in str(err.value)

    # Positional params
    contract_1_address = await account_client.deploy_contract(
        DeployerConfig(
            class_hash=class_hash,
            constructor_calldata=[value, tuple_value, arr, struct],
        ),
        abi=abi,
        deployer_address=deployer_address,
        max_fee=MAX_FEE,
    )
    contract_1 = Contract(address=contract_1_address, abi=abi, client=account_client)

    # Named params
    contract_2_address = await account_client.deploy_contract(
        DeployerConfig(
            class_hash=class_hash,
            constructor_calldata={
                "single_value": value,
                "tuple": tuple_value,
                "arr": arr,
                "dict": struct,
            },
        ),
        abi=abi,
        deployer_address=deployer_address,
        max_fee=MAX_FEE,
    )
    contract_2 = Contract(address=contract_2_address, abi=abi, client=account_client)

    assert contract_1.address != contract_2.address

    result_1 = await contract_1.functions["get"].call(block_hash="latest")
    result_2 = await contract_1.functions["get"].call(block_hash="latest")

    assert result_1 == (value, tuple_value, sum(arr), struct)
    assert result_2 == (value, tuple_value, sum(arr), struct)
