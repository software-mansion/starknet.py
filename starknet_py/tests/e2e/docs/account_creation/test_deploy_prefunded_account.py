import pytest

from starknet_py.net.client import Client
from starknet_py.net.client_models import PriceUnit
from starknet_py.tests.e2e.fixtures.accounts import mint_token_on_devnet
from starknet_py.tests.e2e.utils import _get_random_private_key_unsafe


@pytest.mark.asyncio
async def test_deploy_prefunded_account(
    account_with_validate_deploy_class_hash: int,
    client: Client,
):
    # pylint: disable=import-outside-toplevel, too-many-locals, unused-variable
    full_node_client_fixture = client
    # docs: start
    from starknet_py.hash.address import compute_address
    from starknet_py.net.account.account import Account
    from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping
    from starknet_py.net.full_node_client import FullNodeClient
    from starknet_py.net.signer.key_pair import KeyPair

    # First, make sure to generate private key and salt
    # docs: end
    private_key = _get_random_private_key_unsafe()
    salt = 1
    class_hash = account_with_validate_deploy_class_hash
    # docs: start
    key_pair = KeyPair.from_private_key(private_key)

    # You can also generate a key pair
    key_pair_generated = KeyPair.generate()

    # Compute an address
    address = compute_address(
        salt=salt,
        class_hash=class_hash,  # class_hash of the Account declared on the Starknet
        constructor_calldata=[key_pair.public_key],
        deployer_address=0,
    )

    # Prefund the address (using the token bridge or by sending fee tokens to the computed address)
    # Make sure the tx has been accepted on L2 before proceeding

    # Define the client to be used to interact with Starknet
    client = FullNodeClient(node_url="https://your.node.url")
    # docs: end

    client = full_node_client_fixture
    client_url = client.url.replace("/rpc", "")
    await mint_token_on_devnet(client_url, address, int(1e24), PriceUnit.FRI.value)

    # docs: start

    # Use `Account.deploy_account_v3` static method to deploy an account
    account_deployment_result = await Account.deploy_account_v3(
        address=address,
        class_hash=class_hash,
        salt=salt,
        key_pair=key_pair,
        client=client,
        constructor_calldata=[key_pair.public_key],
        resource_bounds=ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e6), max_price_per_unit=int(1e17)),
            l1_data_gas=ResourceBounds(
                max_amount=int(1e5), max_price_per_unit=int(1e13)
            ),
        ),
    )
    # Wait for deployment transaction to be accepted
    await account_deployment_result.wait_for_acceptance()

    # From now on, account can be used as usual
    account = account_deployment_result.account
    # docs: end
    assert account.address == address
