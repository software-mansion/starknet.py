import pytest

from starknet_py.contract import Contract
from starknet_py.net.client import Client
from starknet_py.net.models import chain_from_network
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE
from starknet_py.tests.e2e.utils import _get_random_private_key_unsafe


@pytest.mark.asyncio
async def test_deploy_prefunded_account(
    account_with_validate_deploy_class_hash: int,
    network: str,
    fee_contract: Contract,
    gateway_client: Client,
):
    # pylint: disable=import-outside-toplevel, too-many-locals
    # docs: start
    from starknet_py.hash.address import compute_address
    from starknet_py.net.account.account import Account
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.net.models import StarknetChainId
    from starknet_py.net.networks import TESTNET
    from starknet_py.net.signer.stark_curve_signer import KeyPair

    # First, make sure to generate private key and salt
    # docs: end
    private_key = _get_random_private_key_unsafe()
    salt = 1
    class_hash = account_with_validate_deploy_class_hash
    # docs: start

    key_pair = KeyPair.from_private_key(private_key)

    # Compute an address
    address = compute_address(
        salt=salt,
        class_hash=class_hash,  # class_hash of the Account declared on the StarkNet
        constructor_calldata=[key_pair.public_key],
        deployer_address=0,
    )

    # Prefund the address (using the token bridge or by sending fee tokens to the computed address)
    # Make sure the tx has been accepted on L2 before proceeding
    # docs: end
    res = await fee_contract.functions["transfer"].invoke(
        recipient=address, amount=int(1e15), max_fee=MAX_FEE
    )
    await res.wait_for_acceptance()
    # docs: start

    # Define the client to be used to interact with StarkNet
    client = GatewayClient(net=TESTNET)
    chain = StarknetChainId.TESTNET
    # docs: end

    client = gateway_client
    chain = chain_from_network(net=network, chain=StarknetChainId.TESTNET)
    # docs: start

    # Use `Account.deploy_account` static method to deploy an account
    account_deployment_result = await Account.deploy_account(
        address=address,
        class_hash=class_hash,
        salt=salt,
        key_pair=key_pair,
        client=client,
        chain=chain,
        constructor_calldata=[key_pair.public_key],
        max_fee=int(1e15),
    )
    # Wait for deployment transaction to be accepted
    await account_deployment_result.wait_for_acceptance()

    # From now on, account can be used as usual
    account = account_deployment_result.account
    # docs: end
    assert account.address == address
