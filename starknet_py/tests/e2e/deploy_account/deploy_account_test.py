import pytest

from starknet_py.net import AccountClient
from starknet_py.net.models import StarknetChainId
from starknet_py.tests.e2e.account.account_client_test import MAX_FEE


@pytest.mark.asyncio
async def test_general_flow(client, deploy_account_details_factory):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()

    account = AccountClient(
        address=address,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
        supported_tx_version=1,
    )

    deploy_account_tx = await account.sign_deploy_account_transaction(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=[key_pair.public_key],
        max_fee=MAX_FEE,
    )
    resp = await account.deploy_account(transaction=deploy_account_tx)

    assert resp.address == address


@pytest.mark.asyncio
async def test_throws_on_transaction_version_0(gateway_account_client):
    with pytest.raises(ValueError) as err:
        await gateway_account_client.sign_deploy_account_transaction(
            class_hash=2, contract_address_salt=1, constructor_calldata=[3], max_fee=7
        )

    assert (
        "Signing deploy account transactions is only supported with transaction version 1"
        in str(err.value)
    )
