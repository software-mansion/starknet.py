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
    # pylint: disable=unused-variable, import-outside-toplevel
    # add to docs: start
    from starknet_py.net.udc_deployer.deployer import Deployer

    # add to docs: end
    testnet_account_client = AccountClient(
        address=123,
        client=GatewayClient(net="testnet"),
        key_pair=KeyPair.from_private_key(123),
        chain=StarknetChainId.TESTNET,
    )

    # add to docs: start
    # If the account is deployed on testnet or mainnet there is no need to explicitly specify
    # address of the deployer (default one will be used)
    deployer = Deployer(account=testnet_account_client)

    # If custom net is used (e.g. starknet-devnet) address of the deployer contract is required
    deployer = Deployer(account=account_client, address=deployer_address)

    # add to docs: end
    salt = None

    # add to docs: start
    # Deployer has two more optional parameters `salt` and `unique`,
    # read about them in the API section
    deployer = Deployer(
        account=account_client, address=deployer_address, salt=salt, unique=False
    )

    # If contract we want to deploy does not have constructor, or the constructor
    # does not have arguments, abi does not have to be passed to the `.make_deployment` method
    deploy_invoke_transaction = await deployer.make_deployment(
        class_hash=map_class_hash
    ).prepare_transaction(max_fee=int(1e16))

    # add to docs: end
    contract_with_constructor_class_hash = constructor_with_arguments_class_hash
    contract_with_constructor_abi = constructor_with_arguments_abi

    # add to docs: start
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
    # abi needs to be passed to `.make_deployment`
    deploy_invoke_transaction = await deployer.make_deployment(
        class_hash=contract_with_constructor_class_hash,
        abi=contract_with_constructor_abi,
    ).prepare_transaction(
        constructor_calldata={
            "single_value": 10,
            "tuple": (1, (2, 3)),
            "arr": [1, 2, 3],
            "dict": {"value": 12, "nested_struct": {"value": 99}},
        },
        max_fee=int(1e16),
    )

    # When transaction is prepared it can be sent with an Account
    resp = await account_client.send_transaction(transaction=deploy_invoke_transaction)
    await account_client.wait_for_tx(resp.transaction_hash)

    # `Deployer.get_deployed_contract_address` is used to get an address of the deployed contract
    # It takes a hash of the transaction which deployed a contract
    address = await deployer.get_deployed_contract_address(
        transaction_hash=resp.transaction_hash
    )
    # add to docs: end

    assert address != 0
