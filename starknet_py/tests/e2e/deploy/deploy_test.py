import pytest

from starknet_py.contract import Contract, ContractFunction
from starknet_py.net.udc_deployer.deployer import Deployer
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
    deployer = Deployer(account=account_client, deployer_address=deployer_address)

    deploy_invoke_tx = await deployer.prepare_contract_deployment(
        class_hash=map_class_hash, max_fee=MAX_FEE
    )

    resp = await account_client.send_transaction(deploy_invoke_tx)
    await account_client.wait_for_tx(resp.transaction_hash)

    deployed_contract_address = await deployer.find_deployed_contract_address(
        transaction_hash=resp.transaction_hash
    )

    assert isinstance(deployed_contract_address, int)
    assert deployed_contract_address != 0


@pytest.mark.asyncio
async def test_throws_when_deployer_address_not_specified_on_custom_network(
    account_client,
):
    with pytest.raises(ValueError) as err:
        Deployer(account=account_client)

    assert "deployer_address is required when not using predefined networks." in str(
        err.value
    )


@pytest.mark.asyncio
async def test_throws_when_calldata_provided_without_abi(
    account_client, map_class_hash, deployer_address
):
    deployer = Deployer(account=account_client, deployer_address=deployer_address)

    with pytest.raises(ValueError) as err:
        await deployer.prepare_contract_deployment(
            class_hash=map_class_hash, calldata=[12, 34]
        )

    assert "calldata was provided without an abi" in str(err.value)


@pytest.mark.asyncio
async def test_throws_when_calldata_not_provided(
    account_client, deployer_address, constructor_with_arguments_abi
):
    deployer = Deployer(account=account_client, deployer_address=deployer_address)

    with pytest.raises(ValueError) as err:
        await deployer.prepare_contract_deployment(
            class_hash=1234, abi=constructor_with_arguments_abi
        )

    assert "Provided contract has a constructor and no arguments were provided." in str(
        err.value
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "calldata",
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
    calldata,
):
    deployer = Deployer(account=account_client, deployer_address=deployer_address)

    deploy_invoke_transaction = await deployer.prepare_contract_deployment(
        class_hash=constructor_with_arguments_class_hash,
        abi=constructor_with_arguments_abi,
        calldata=calldata,
        max_fee=MAX_FEE,
    )

    resp = await account_client.send_transaction(deploy_invoke_transaction)
    await account_client.wait_for_tx(resp.transaction_hash)

    contract_address = await deployer.find_deployed_contract_address(
        transaction_hash=resp.transaction_hash
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


@pytest.mark.asyncio
async def test_throws_when_wrong_tx_hash_provided(
    gateway_account_client, deployer_address, put_with_event_transaction_hash
):
    deployer = Deployer(
        account=gateway_account_client, deployer_address=deployer_address
    )

    with pytest.raises(ValueError) as err:
        await deployer.find_deployed_contract_address(
            transaction_hash=put_with_event_transaction_hash
        )

    assert "ContractDeployed event was not found." in str(err.value)
