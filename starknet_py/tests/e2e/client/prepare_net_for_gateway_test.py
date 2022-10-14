from dataclasses import dataclass

from starknet_py.contract import Contract
from starknet_py.net import AccountClient
from starknet_py.net.client import Client
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.tests.e2e.conftest import AccountToBeDeployedDetails


@dataclass
class PreparedNetworkData:
    # pylint: disable=too-many-instance-attributes
    contract_address: int
    deploy_transaction_hash: int
    block_with_deploy_number: int
    block_with_deploy_hash: int
    invoke_transaction_hash: int
    block_with_invoke_number: int
    declare_transaction_hash: int
    block_with_declare_number: int
    deploy_account_transaction_hash: int
    block_with_deploy_account_number: int
    block_with_deploy_account_hash: int


async def prepare_net_for_tests(
    account_client: AccountClient,
    compiled_contract: str,
    deploy_account_details: AccountToBeDeployedDetails,
) -> PreparedNetworkData:
    # pylint: disable=too-many-locals

    deployment_result = await Contract.deploy(
        client=account_client, compiled_contract=compiled_contract
    )
    deployment_result = await deployment_result.wait_for_acceptance(
        wait_for_accept=True
    )
    contract = deployment_result.deployed_contract

    deploy_receipt = await account_client.get_transaction_receipt(
        deployment_result.hash
    )
    block_with_deploy_number = deploy_receipt.block_number
    block_with_deploy_hash = deploy_receipt.block_hash

    invoke_res = await contract.functions["increase_balance"].invoke(
        amount=1234, max_fee=int(1e20)
    )
    await invoke_res.wait_for_acceptance()

    block_with_invoke_number = (
        await account_client.get_transaction_receipt(invoke_res.hash)
    ).block_number

    declare_tx = await account_client.sign_declare_transaction(
        compiled_contract=compiled_contract, max_fee=int(1e16)
    )
    declare_result = await account_client.declare(declare_tx)
    await account_client.wait_for_tx(declare_result.transaction_hash)

    block_with_declare_number = (
        await account_client.get_transaction_receipt(declare_result.transaction_hash)
    ).block_number

    deploy_account_tx = await _signed_deploy_account_transaction(
        account_client.client, deploy_account_details
    )
    deploy_account_result = await account_client.deploy_prefunded(deploy_account_tx)
    await account_client.wait_for_tx(deploy_account_result.transaction_hash)

    declare_account_receipt = await account_client.get_transaction_receipt(
        deploy_account_result.transaction_hash
    )
    block_with_deploy_account_number = declare_account_receipt.block_number
    block_with_deploy_account_hash = declare_account_receipt.block_hash

    assert block_with_deploy_number is not None
    assert block_with_deploy_hash is not None
    assert block_with_invoke_number is not None
    assert block_with_declare_number is not None
    assert block_with_deploy_account_number is not None
    assert block_with_deploy_account_hash is not None

    return PreparedNetworkData(
        contract_address=contract.address,
        deploy_transaction_hash=deployment_result.hash,
        block_with_deploy_number=block_with_deploy_number,
        block_with_deploy_hash=block_with_deploy_hash,
        invoke_transaction_hash=invoke_res.hash,
        block_with_invoke_number=block_with_invoke_number,
        declare_transaction_hash=declare_result.transaction_hash,
        block_with_declare_number=block_with_declare_number,
        deploy_account_transaction_hash=deploy_account_result.transaction_hash,
        block_with_deploy_account_hash=block_with_deploy_account_hash,
        block_with_deploy_account_number=block_with_deploy_account_number,
    )


async def _signed_deploy_account_transaction(
    client: Client, details: AccountToBeDeployedDetails
) -> DeployAccount:
    """
    Create a signed DEPLOY_ACCOUNT transaction using account details
    """
    address, key_pair, salt, class_hash = details
    account_client = AccountClient(
        address=address,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET,
        supported_tx_version=1,
    )
    return await account_client.sign_deploy_account_transaction(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=[key_pair.public_key],
        max_fee=int(1e16),
    )
