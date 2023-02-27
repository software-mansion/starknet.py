import pytest

from starknet_py.net.account.account import Account
from starknet_py.net.models import StarknetChainId
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE


@pytest.mark.asyncio
async def test_declare(account, map_compiled_contract):
    declare_tx = await account.sign_declare_transaction(
        compiled_contract=map_compiled_contract, max_fee=MAX_FEE
    )
    result = await account.client.declare(declare_tx)

    await account.client.wait_for_tx(
        tx_hash=result.transaction_hash, wait_for_accept=True
    )


@pytest.mark.asyncio
async def test_default_deploy_with_class_hash(account, map_class_hash):
    deployer = Deployer()

    contract_deployment = deployer.create_deployment_call(class_hash=map_class_hash)

    deploy_invoke_tx = await account.sign_invoke_transaction(
        contract_deployment.call, max_fee=MAX_FEE
    )
    resp = await account.client.send_transaction(deploy_invoke_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    assert isinstance(contract_deployment.address, int)
    assert contract_deployment.address != 0


@pytest.mark.asyncio
async def test_deploy_account(client, deploy_account_details_factory):
    address, key_pair, salt, class_hash = await deploy_account_details_factory.get()

    account = Account(
        address=address,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
    )

    deploy_account_tx = await account.sign_deploy_account_transaction(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=[key_pair.public_key],
        max_fee=MAX_FEE,
    )
    resp = await account.client.deploy_account(transaction=deploy_account_tx)

    assert resp.address == address


@pytest.mark.asyncio
async def test_invoke_and_call(map_contract):
    invocation = await map_contract.functions["put"].invoke(2, 13, max_fee=MAX_FEE)
    await invocation.wait_for_acceptance(wait_for_accept=True)
    (response,) = await map_contract.functions["get"].call(2)

    assert response == 13
