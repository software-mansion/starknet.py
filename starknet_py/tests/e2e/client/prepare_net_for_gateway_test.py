from starknet_py.contract import Contract
from starknet_py.net import AccountClient
from starknet_py.transactions.declare import make_declare_tx


async def prepare_net_for_tests(account_client: AccountClient, compiled_contract: str):
    # pylint: disable=no-member, too-many-locals
    deployment_result = await Contract.deploy(
        client=account_client, compiled_contract=compiled_contract
    )
    deployment_result = await deployment_result.wait_for_acceptance(
        wait_for_accept=True
    )
    contract = deployment_result.deployed_contract

    contract_address = contract.address
    deploy_transaction_hash = deployment_result.hash
    deploy_receipt = await account_client.get_transaction_receipt(
        deploy_transaction_hash
    )
    block_with_deploy_number = deploy_receipt.block_number
    block_with_deploy_hash = deploy_receipt.block_hash

    invoke_res = await contract.functions["increase_balance"].invoke(
        amount=1234, max_fee=int(1e20)
    )
    await invoke_res.wait_for_acceptance()

    invoke_transaction_hash = invoke_res.hash
    block_with_invoke_number = (
        await account_client.get_transaction_receipt(invoke_transaction_hash)
    ).block_number

    declare_tx = make_declare_tx(compiled_contract=compiled_contract)
    declare_result = await account_client.declare(declare_tx)
    await account_client.wait_for_tx(declare_result.transaction_hash)

    declare_transaction_hash = declare_result.transaction_hash
    block_with_declare_number = (
        await account_client.get_transaction_receipt(declare_transaction_hash)
    ).block_number

    return (
        contract_address,
        deploy_transaction_hash,
        block_with_deploy_number,
        block_with_deploy_hash,
        invoke_transaction_hash,
        block_with_invoke_number,
        declare_transaction_hash,
        block_with_declare_number,
    )
