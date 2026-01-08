import pytest

from starknet_py.common import create_casm_class
from starknet_py.constants import ARGENT_V040_CLASS_HASH, STRK_FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.account.account import Account
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.client_models import (
    Call,
    DeployAccountTransactionV3,
    TransactionExecutionStatus,
)
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.udc_deployer.deployer import Deployer, _get_random_salt
from starknet_py.tests.e2e.fixtures.misc import ContractVersion, load_contract
from starknet_py.tests.e2e.utils import _new_address


@pytest.mark.asyncio
async def test_execute_v3(account_sepolia_testnet):
    # https://sepolia.starkscan.co/contract/0x0589A8B8BF819B7820CB699EA1F6C409BC012C9B9160106DDC3DACD6A89653CF
    sepolia_balance_contract_address = (
        0x0589A8B8BF819B7820CB699EA1F6C409BC012C9B9160106DDC3DACD6A89653CF
    )

    increase_balance_call = Call(
        to_addr=sepolia_balance_contract_address,
        selector=get_selector_from_name("increase_balance"),
        calldata=[100],
    )

    tx_response = await account_sepolia_testnet.execute_v3(
        calls=increase_balance_call, auto_estimate=True
    )
    receipt = await account_sepolia_testnet.client.wait_for_tx(
        tx_hash=tx_response.transaction_hash
    )

    assert receipt.execution_status == TransactionExecutionStatus.SUCCEEDED
    assert receipt.transaction_hash == tx_response.transaction_hash


@pytest.mark.asyncio
async def test_deploy_account_v3(
    account_sepolia_testnet,
    client_sepolia_testnet,
):
    key_pair = KeyPair.generate()
    constructor_calldata = [0, key_pair.public_key, 1]
    address, salt = _new_address(ARGENT_V040_CLASS_HASH, constructor_calldata)

    new_account = Account(
        address=address,
        client=client_sepolia_testnet,
        key_pair=key_pair,
        chain=StarknetChainId.SEPOLIA,
    )

    # Estimate account deployment fee
    tx = await new_account.sign_deploy_account_v3(
        class_hash=ARGENT_V040_CLASS_HASH,
        contract_address_salt=salt,
        constructor_calldata=constructor_calldata,
        auto_estimate=True,
    )
    deploy_account_fee = await new_account.estimate_fee(tx=tx)
    deploy_account_fee = (
        deploy_account_fee[0]
        if isinstance(deploy_account_fee, list)
        else deploy_account_fee
    )

    contract = await Contract.from_address(
        provider=account_sepolia_testnet, address=STRK_FEE_CONTRACT_ADDRESS
    )

    # Prefund account with 5 * deployment fee
    invocation = await contract.functions["transfer"].invoke_v3(
        address, deploy_account_fee.overall_fee * 5, auto_estimate=True
    )
    await invocation.wait_for_acceptance()

    deploy_result = await Account.deploy_account_v3(
        address=address,
        class_hash=ARGENT_V040_CLASS_HASH,
        salt=salt,
        key_pair=key_pair,
        client=client_sepolia_testnet,
        constructor_calldata=constructor_calldata,
        auto_estimate=True,
    )
    await deploy_result.wait_for_acceptance()

    assert isinstance(account_sepolia_testnet, BaseAccount)
    assert deploy_result.account.address == address

    transaction = await client_sepolia_testnet.get_transaction(
        tx_hash=deploy_result.hash
    )
    assert isinstance(transaction, DeployAccountTransactionV3)
    assert transaction.constructor_calldata == constructor_calldata


@pytest.mark.asyncio
async def test_declare_v3(account_sepolia_testnet):
    contract = load_contract(contract_name="SaltedContract", version=ContractVersion.V2)

    compiled_contract = contract["sierra"]
    compiled_class_hash = compute_casm_class_hash(create_casm_class(contract["casm"]))
    signed_tx = await account_sepolia_testnet.sign_declare_v3(
        compiled_contract,
        compiled_class_hash,
        auto_estimate=True,
    )

    declare_response = await account_sepolia_testnet.client.declare(
        transaction=signed_tx
    )
    await account_sepolia_testnet.client.wait_for_tx(declare_response.transaction_hash)

    assert declare_response.class_hash != 0


@pytest.mark.asyncio
async def test_deploy_v3(account_sepolia_testnet):
    calldata = []
    salt = _get_random_salt()

    deployer = Deployer()

    # https://sepolia.starkscan.co/class/0x0227f52a4d2138816edf8231980d5f9e6e0c8a3deab45b601a1fcee3d4427b02
    example_contract_sepolia_class_hash = (
        0x0227F52A4D2138816EDF8231980D5F9E6E0C8A3DEAB45B601A1FCEE3D4427B02
    )
    contract_deployment = deployer.create_contract_deployment(
        class_hash=example_contract_sepolia_class_hash,
        cairo_version=1,
        calldata=calldata,
        salt=salt,
    )

    res = await account_sepolia_testnet.execute_v3(
        calls=contract_deployment.call, auto_estimate=True
    )
    await account_sepolia_testnet.client.wait_for_tx(res.transaction_hash)

    assert isinstance(contract_deployment.address, int)
    assert contract_deployment.address != 0
