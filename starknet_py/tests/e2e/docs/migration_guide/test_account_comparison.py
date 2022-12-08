import pytest

from starknet_py.net.client_models import Call


@pytest.mark.asyncio
async def test_account_comparison(
    gateway_account, gateway_account_client, base_account_deploy_map_contract
):
    address = base_account_deploy_map_contract.address
    key = 0x111
    account_client = gateway_account_client
    account = gateway_account

    # docs-1: start
    # Inspecting storage

    await account_client.get_storage_at(contract_address=address, key=key)

    # becomes

    await account.client.get_storage_at(contract_address=address, key=key)
    # docs-1: end

    call = Call(to_addr=0x1, selector=0x1234, calldata=[])
    max_fee = 1000

    # docs-2: start
    # Sending transactions

    tx = await account_client.sign_invoke_transaction(call, max_fee)
    await account_client.send_transaction(tx)

    # becomes

    tx = await account.sign_invoke_transaction(call, max_fee=max_fee)
    # Note that max_fee is now keyword-only argument
    await account.client.send_transaction(tx)
    # docs-2: end

    # docs-3: start
    # Using execute method

    await account_client.execute(call, max_fee)

    # becomes

    await account.execute(call, max_fee=max_fee)
    # docs-3: end
