import sys

import pytest


@pytest.mark.skipif(
    "--contract_dir=v2" not in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_deploying_with_udc(
    account,
    map_class_hash,
    constructor_with_arguments_abi,
    constructor_with_arguments_class_hash,
):
    # pylint: disable=unused-variable, import-outside-toplevel, too-many-locals
    # docs: start
    from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping
    from starknet_py.net.udc_deployer.deployer import Deployer

    # docs: end
    deployer_address = "0x123"
    salt = None

    # docs: start
    # If you use mainnet/sepolia there is no need to explicitly specify
    # address of the deployer (default one will be used)
    deployer = Deployer()

    # If custom network is used address of the deployer contract is required
    deployer = Deployer(deployer_address=deployer_address)

    # Deployer has one more optional parameter `account_address`
    # It is used to salt address of the contract with address of an account which deploys it
    deployer = Deployer(account_address=account.address)

    # If contract we want to deploy does not have constructor, or the constructor
    # does not have arguments, abi is not a required parameter of `deployer.create_contract_deployment` method
    deploy_call, address = deployer.create_contract_deployment(
        class_hash=map_class_hash, salt=salt
    )

    # docs: end
    contract_with_constructor_class_hash = constructor_with_arguments_class_hash
    contract_with_constructor_abi = constructor_with_arguments_abi

    # docs: start
    contract_constructor = """
    #[constructor]
    fn constructor(ref self: ContractState, single_value: felt252, tuple: (felt252, (felt252, felt252)), arr: Array<felt252>, dict: TopStruct) {
        let mut sum = 0;
        let count = arr.len();
        let mut i: usize = 0;
        while i != count {
            let element: felt252 = arr[i].clone();
            sum += element;
            i += 1;
        };

        self.single_value.write(single_value);
        self.tuple.write(tuple);
        self.arr_sum.write(sum);
        self.dict.write(dict);
    }
    """

    # If contract constructor accepts arguments, as shown above,
    # abi needs to be passed to `deployer.create_contract_deployment`
    # Note that this method also returns address of the contract we want to deploy
    deploy_call, address = deployer.create_contract_deployment(
        class_hash=contract_with_constructor_class_hash,
        abi=constructor_with_arguments_abi,
        cairo_version=1,
        calldata={
            "single_value": 10,
            "tuple": (1, (2, 3)),
            "arr": [1, 2, 3],
            "dict": {"value": 12, "nested_struct": {"value": 99}},
        },
    )

    # Once call is prepared, it can be executed with an account (preferred way)
    resp = await account.execute_v3(
        deploy_call,
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17)),
            l1_data_gas=ResourceBounds(
                max_amount=int(1e5), max_price_per_unit=int(1e13)
            ),
        ),
    )

    # docs: end
    deploy_call, _ = deployer.create_contract_deployment(
        class_hash=contract_with_constructor_class_hash,
        abi=constructor_with_arguments_abi,
        calldata={
            "single_value": 0,
            "tuple": (1, (2, 3)),
            "arr": [1],
            "dict": {"value": 12, "nested_struct": {"value": 99}},
        },
    )
    # docs: start
    # Or signed and send with an account
    invoke_tx = await account.sign_invoke_v3(
        deploy_call,
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17)),
            l1_data_gas=ResourceBounds(
                max_amount=int(1e5), max_price_per_unit=int(1e13)
            ),
        ),
    )
    resp = await account.client.send_transaction(invoke_tx)

    # Wait for transaction
    await account.client.wait_for_tx(resp.transaction_hash)

    # After waiting for a transaction
    # contract is accessible at the address returned by `deployer.create_deployment_call`
    # docs: end

    assert address != 0
