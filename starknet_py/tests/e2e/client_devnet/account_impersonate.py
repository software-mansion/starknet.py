import pytest

from starknet_py.contract import Contract
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.tests.e2e.fixtures.misc import ContractVersion, load_contract


async def get_contract_address(account: BaseAccount):
    compiled_contract = load_contract(
        contract_name="TestContract", version=ContractVersion.V1
    )
    declare_result = await Contract.declare_v2(
        account,
        compiled_contract=compiled_contract["sierra"],
        compiled_contract_casm=compiled_contract["casm"],
        max_fee=int(1e18),
    )
    await declare_result.wait_for_acceptance()

    deploy_result = await declare_result.deploy_v1(max_fee=int(1e18))
    await deploy_result.wait_for_acceptance()

    return deploy_result.deployed_contract.address


@pytest.mark.asyncio
async def test_impersonated_account(
    devnet_forking_mode_client, impersonated_account, forked_devnet_account
):
    await devnet_forking_mode_client.impersonate_account(
        address=impersonated_account.address
    )

    contract_address = await get_contract_address(forked_devnet_account)

    contract = await Contract.from_address(
        provider=impersonated_account, address=contract_address
    )

    inv = await contract.functions["test"].invoke_v1(
        "0x1", "0x1", "0x1", auto_estimate=True
    )

    assert inv.invoke_transaction.sender_address == impersonated_account.address
