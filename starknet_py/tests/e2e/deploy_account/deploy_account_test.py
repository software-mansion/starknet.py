import pytest

from starknet_py.net.account.account import Account
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import DeployAccountV3
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS


@pytest.mark.asyncio
async def test_general_flow(client, deploy_account_details_factory):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()

    account = Account(
        address=address,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.SEPOLIA,
    )

    deploy_account_tx = await account.sign_deploy_account_v3(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=[key_pair.public_key],
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    resp = await account.client.deploy_account(transaction=deploy_account_tx)

    assert resp.address == address


@pytest.mark.asyncio
async def test_deploy_account_v3(client, deploy_account_details_factory):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()

    account = Account(
        address=address,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.SEPOLIA,
    )

    deploy_account_tx = await account.sign_deploy_account_v3(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=[key_pair.public_key],
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )

    assert isinstance(deploy_account_tx, DeployAccountV3)

    resp = await account.client.deploy_account(transaction=deploy_account_tx)

    assert resp.address == address
