from dataclasses import dataclass

from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.tests.e2e.utils import (
    AccountToBeDeployedDetails,
    get_deploy_account_transaction,
)


@dataclass
class PreparedNetworkData:
    # pylint: disable=too-many-instance-attributes
    class_hash: int
    contract_address: int
    contract_address_2: int
    invoke_transaction_hash: int
    block_with_invoke_number: int
    declare_transaction_hash: int
    block_with_declare_number: int
    block_with_declare_hash: int
    deploy_account_transaction_hash: int
    block_with_deploy_account_number: int
    block_with_deploy_account_hash: int


async def prepare_net_for_tests(
    account: Account,
    deploy_account_details: AccountToBeDeployedDetails,
    transaction_hash: int,
    contract: Contract,
    contract_2: Contract,
    declare_class_hash: int,
) -> PreparedNetworkData:
    # pylint: disable=too-many-locals

    declare_receipt = await account.client.get_transaction_receipt(transaction_hash)
    block_with_declare_number = declare_receipt.block_number
    block_with_declare_hash = declare_receipt.block_hash

    invoke_res = await contract.functions["increase_balance"].invoke_v3(
        amount=1777, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await invoke_res.wait_for_acceptance()

    invoke_res_2 = await contract_2.functions["increase_balance"].invoke_v3(
        amount=1777, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await invoke_res_2.wait_for_acceptance()

    block_with_invoke_number = (
        await account.client.get_transaction_receipt(invoke_res.hash)
    ).block_number
    block_with_invoke_number_2 = (
        await account.client.get_transaction_receipt(invoke_res_2.hash)
    ).block_number

    address, key_pair, salt, class_hash = deploy_account_details
    deploy_account_tx = await get_deploy_account_transaction(
        address=address,
        key_pair=key_pair,
        salt=salt,
        class_hash=class_hash,
        client=account.client,
    )
    deploy_account_result = await account.client.deploy_account(deploy_account_tx)
    await account.client.wait_for_tx(deploy_account_result.transaction_hash)

    declare_account_receipt = await account.client.get_transaction_receipt(
        deploy_account_result.transaction_hash
    )
    block_with_deploy_account_number = declare_account_receipt.block_number
    block_with_deploy_account_hash = declare_account_receipt.block_hash

    assert block_with_invoke_number is not None
    assert block_with_invoke_number_2 is not None
    assert block_with_declare_number is not None
    assert block_with_declare_hash is not None
    assert block_with_deploy_account_number is not None
    assert block_with_deploy_account_hash is not None

    return PreparedNetworkData(
        class_hash=declare_class_hash,
        contract_address=contract.address,
        contract_address_2=contract_2.address,
        invoke_transaction_hash=invoke_res.hash,
        block_with_invoke_number=block_with_invoke_number,
        declare_transaction_hash=transaction_hash,
        block_with_declare_number=block_with_declare_number,
        block_with_declare_hash=block_with_declare_hash,
        deploy_account_transaction_hash=deploy_account_result.transaction_hash,
        block_with_deploy_account_hash=block_with_deploy_account_hash,
        block_with_deploy_account_number=block_with_deploy_account_number,
    )
