import pytest

from starknet_py.contract import Contract, ContractFunction
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

    assert "no arguments were provided" in str(err.value)

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
    contract_deployment = account_client.create_deployer(
        deployer_address=deployer_address
    ).for_contract(class_hash=map_class_hash)

    deploy_invoke_tx = await contract_deployment.prepare_transaction(max_fee=MAX_FEE)
    deployed_contract_address = await contract_deployment.send_transaction(
        deploy_invoke_transaction=deploy_invoke_tx
    )

    assert isinstance(deployed_contract_address, int)
    assert deployed_contract_address != 0


@pytest.mark.asyncio
async def test_throws_when_deployer_address_not_specified_on_custom_network(
    account_client,
):
    with pytest.raises(ValueError) as err:
        account_client.create_deployer()

    assert "deployer_address is required when not using predefined networks." in str(
        err.value
    )


@pytest.mark.asyncio
async def test_throws_when_constructor_calldata_without_abi(
    account_client, map_class_hash, deployer_address
):
    contract_deployment = account_client.create_deployer(
        deployer_address=deployer_address
    ).for_contract(class_hash=map_class_hash)

    with pytest.raises(ValueError) as err:
        await contract_deployment.prepare_transaction(constructor_calldata=[12, 34])

    assert "constructor_calldata was provided without an abi" in str(err.value)


@pytest.mark.asyncio
async def test_throws_when_constructor_calldata_not_provided(
    account_client, deployer_address, constructor_with_arguments_abi
):
    contract_deployment = account_client.create_deployer(
        deployer_address=deployer_address
    ).for_contract(class_hash=1234, abi=constructor_with_arguments_abi)

    with pytest.raises(ValueError) as err:
        await contract_deployment.prepare_transaction()

    assert "Provided contract has a constructor and no arguments were provided." in str(
        err.value
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "constructor_calldata",
    [
        [10, (1, (2, 3)), [1, 2, 3], {"value": 12, "nested_struct": {"value": 99}}],
        {
            "single_value": 10,
            "tuple": (1, (2, 3)),
            "arr": [1, 2, 3],
            "dict": {"value": 12, "nested_struct": {"value": 99}},
        },
    ],
)
async def test_constructor_arguments_contract_deploy(
    account_client,
    deployer_address,
    constructor_with_arguments_abi,
    constructor_with_arguments_class_hash,
    constructor_calldata,
):
    contract_deployer = account_client.create_deployer(
        deployer_address=deployer_address
    ).for_contract(
        class_hash=constructor_with_arguments_class_hash,
        abi=constructor_with_arguments_abi,
    )

    deploy_invoke_transaction = await contract_deployer.prepare_transaction(
        constructor_calldata=constructor_calldata, max_fee=MAX_FEE
    )
    contract_address = await contract_deployer.send_transaction(
        deploy_invoke_transaction=deploy_invoke_transaction
    )

    contract = Contract(
        address=contract_address,
        abi=constructor_with_arguments_abi,
        client=account_client,
    )

    result = await contract.functions["get"].call(block_hash="latest")

    assert result == (
        10,
        (1, (2, 3)),
        sum([1, 2, 3]),
        {"value": 12, "nested_struct": {"value": 99}},
    )
