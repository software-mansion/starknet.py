import pytest

from starknet_py.net.client_models import ResourceBounds


@pytest.mark.asyncio
async def test_simple_deploy(account, hello_starknet_class_hash, hello_starknet_abi):
    # pylint: disable=import-outside-toplevel
    # docs: start
    from starknet_py.contract import Contract

    # docs: end

    class_hash = hello_starknet_class_hash
    abi = hello_starknet_abi

    # docs: start
    # To deploy contract just use `Contract.deploy_contract_v1` method
    # Note that class_hash and abi of the contract must be known

    # If constructor of the contract requires arguments, pass constructor_args parameter
    constructor_args = {"value": 10}

    # docs: end
    constructor_args = None

    # docs: start
    deploy_result = await Contract.deploy_contract_v3(
        account=account,
        class_hash=class_hash,
        abi=abi,  # abi is optional
        constructor_args=constructor_args,
        l1_resource_bounds=ResourceBounds(
            max_amount=int(1e5), max_price_per_unit=int(1e13)
        ),
    )

    # `Contract.deploy_contract_v1` and `Contract.deploy_contract_v3` methods have an optional parameter
    # `deployer_address` that needs to be specified when using other network than mainnet or sepolia
    # Read more about it in the API section

    # Wait for the transaction
    await deploy_result.wait_for_acceptance()

    # To interact with just deployed contract get its instance from the deploy_result
    contract = deploy_result.deployed_contract

    # Now, any of the contract functions can be called
    # docs: end

    assert contract.address != 0
