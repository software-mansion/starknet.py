import pytest
from starkware.crypto.signature.signature import get_random_private_key
from starkware.starknet.definitions.fields import ContractAddressSalt

from starknet_py.contract import Contract
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


@pytest.mark.asyncio
async def test_deploy_prefunded_account(
    account_with_validate_deploy_class_hash: int, network: str, fee_contract: Contract
):
    # pylint: disable=import-outside-toplevel, too-many-locals
    # docs: start
    from starknet_py.net import KeyPair
    from starknet_py.net.account.account import Account
    from starknet_py.net.gateway_client import GatewayClient
    from starknet_py.net.models import StarknetChainId, compute_address

    # First, make sure to generate private key and salt
    # docs: end
    private_key = get_random_private_key()
    salt = ContractAddressSalt.get_random_value()
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

    # Create an Account instance
    account = Account(
        address=address,
        client=GatewayClient(net=network),
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
    )

    # Create and sign DeployAccount transaction
    deploy_account_tx = await account.sign_deploy_account_transaction(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=[key_pair.public_key],
        max_fee=int(1e15),
    )

    resp = await account.client.deploy_account(transaction=deploy_account_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    # Since this moment account can be used to sign other transactions
    # docs: end

    assert address == resp.address
