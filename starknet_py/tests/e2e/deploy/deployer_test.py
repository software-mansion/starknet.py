import pytest

from starknet_py.contract import Contract
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.net.udc_deployer.errors import ContractDeployedEventNotFound
from starknet_py.tests.e2e.conftest import MAX_FEE


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
    gateway_account_client, deployer_address, transaction_with_event_transaction_hash
):
    deployer = Deployer(
        account=gateway_account_client, deployer_address=deployer_address
    )

    with pytest.raises(ContractDeployedEventNotFound) as err:
        await deployer.find_deployed_contract_address(
            transaction_hash=transaction_with_event_transaction_hash
        )

    assert "ContractDeployed event was not found" in str(err.value)
