from starknet_py.contract import Contract
from starknet_py.net import AccountClient
from starknet_py.transactions.declare import make_declare_tx


def prepare_net_for_tests(account_client: AccountClient, compiled_contract: str):
    # pylint: disable=no-member
    deployment_result = Contract.deploy_sync(
        client=account_client, compiled_contract=compiled_contract
    )
    deployment_result = deployment_result.wait_for_acceptance_sync()
    contract = deployment_result.deployed_contract

    contract_address = contract.address
    deploy_transaction_hash = deployment_result.hash
    block_with_deploy_number = account_client.get_transaction_receipt_sync(
        deploy_transaction_hash
    ).block_number

    invoke_res = contract.functions["increase_balance"].invoke_sync(
        amount=1234, max_fee=int(1e20)
    )
    invoke_res.wait_for_acceptance_sync()

    invoke_transaction_hash = invoke_res.hash
    block_with_invoke_number = account_client.get_transaction_receipt_sync(
        invoke_transaction_hash
    ).block_number

    declare_tx = make_declare_tx(compiled_contract=compiled_contract)
    declare_result = account_client.declare_sync(declare_tx)
    account_client.wait_for_tx_sync(declare_result.transaction_hash)

    declare_transaction_hash = declare_result.transaction_hash
    block_with_declare_number = account_client.get_transaction_receipt_sync(
        declare_transaction_hash
    ).block_number

    return (
        contract_address,
        deploy_transaction_hash,
        block_with_deploy_number,
        invoke_transaction_hash,
        block_with_invoke_number,
        declare_transaction_hash,
        block_with_declare_number,
    )
