import pytest

from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId


@pytest.mark.asyncio
async def test_deploying_with_udc(
    account_client,
    map_class_hash,
    deployer_address,
    constructor_with_arguments_abi,
    constructor_with_arguments_class_hash,
):
    # pylint: disable=unused-variable, import-outside-toplevel, too-many-locals
    # docs: start
    from starknet_py.net.udc_deployer.deployer import Deployer

    # docs: end
    testnet_account_client = AccountClient(
        address=123,
        client=GatewayClient(net="testnet"),
        key_pair=KeyPair.from_private_key(123),
        chain=StarknetChainId.TESTNET,
    )

    # docs: start
    # If you use mainnet/testnet/devnet there is no need to explicitly specify
    # address of the deployer (default one will be used)
    deployer = Deployer()

    # If custom net is used address of the deployer contract is required
    deployer = Deployer(deployer_address=deployer_address)

    # Deployer has one more optional parameter `account_address`
    # It is used to salt address of the contract with address of an account which deploys it
    deployer = Deployer(
        deployer_address=deployer_address, account_address=account_client.address
    )
    # docs: end
    salt = None
    # docs: start

    # If contract we want to deploy does not have constructor, or the constructor
    # does not have arguments, abi is not a required parameter of `deployer.create_deployment_call` method
    deploy_call, address = await deployer.create_deployment_call(
        class_hash=map_class_hash, salt=salt
    )

    # docs: end
    contract_with_constructor_class_hash = constructor_with_arguments_class_hash
    contract_with_constructor_abi = constructor_with_arguments_abi

    # docs: start
    contract_constructor = """
        @constructor
        func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
            single_value: felt, tuple: (felt, (felt, felt)), arr_len: felt, arr: felt*, dict: TopStruct
        ) {
            let (arr_sum) = array_sum(arr, arr_len);
            storage.write((single_value, tuple, arr_sum, dict));
            return ();
        }
    """

    # If contract constructor accepts arguments, as shown above,
    # abi needs to be passed to `deployer.create_deployment_call`
    # Note that this method also returns address of the contract we want to deploy
    deploy_call, address = await deployer.create_deployment_call(
        class_hash=contract_with_constructor_class_hash,
        abi=contract_with_constructor_abi,
        calldata={
            "single_value": 10,
            "tuple": (1, (2, 3)),
            "arr": [1, 2, 3],
            "dict": {"value": 12, "nested_struct": {"value": 99}},
        },
    )

    # Once call is prepared it can be signed and send with an Account
    invoke_tx = await account_client.sign_invoke_transaction(
        deploy_call, max_fee=int(1e16)
    )
    resp = await account_client.send_transaction(transaction=invoke_tx)
    await account_client.wait_for_tx(resp.transaction_hash)

    # After waiting for a transaction
    # contract is accessible at the address returned by `deployer.prepare_contract_deployment`
    # docs: end

    assert address != 0
