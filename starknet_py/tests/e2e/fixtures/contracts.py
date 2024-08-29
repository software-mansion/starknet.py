# pylint: disable=redefined-outer-name
from typing import Any, Dict, List, Optional, Tuple

import pytest
import pytest_asyncio

from starknet_py.common import create_casm_class, create_sierra_compiled_contract
from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import (
    MAX_FEE,
    PRECOMPILED_CONTRACTS_DIR,
    STRK_FEE_CONTRACT_ADDRESS,
)
from starknet_py.tests.e2e.fixtures.misc import (
    ContractVersion,
    load_contract,
    read_contract,
)


@pytest.fixture(scope="package")
def sierra_minimal_compiled_contract_and_class_hash() -> Tuple[str, int]:
    """
    Returns minimal contract compiled to sierra and its compiled class hash.
    """
    contract = load_contract(contract_name="MinimalContract")

    return (
        contract["sierra"],
        compute_casm_class_hash(create_casm_class(contract["casm"])),
    )


@pytest.fixture(scope="package")
def abi_types_compiled_contract_and_class_hash() -> Tuple[str, int]:
    """
    Returns abi_types contract compiled to sierra and its compiled class hash.
    """
    contract = load_contract(contract_name="AbiTypes", version=ContractVersion.V2)

    return (
        contract["sierra"],
        compute_casm_class_hash(create_casm_class(contract["casm"])),
    )


async def deploy_contract(account: BaseAccount, class_hash: int, abi: List) -> Contract:
    """
    Deploys a contract and returns its instance.
    """
    deployment_result = await Contract.deploy_contract_v1(
        account=account, class_hash=class_hash, abi=abi, max_fee=MAX_FEE
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    return deployment_result.deployed_contract


async def deploy_v1_contract(
    account: BaseAccount,
    contract_name: str,
    class_hash: int,
    calldata: Optional[Dict[str, Any]] = None,
) -> Contract:
    """
    Deploys Cairo1.0 contract.

    :param account: An account which will be used to deploy the Contract.
    :param contract_name: Name of the contract from project mocks (e.g. `ERC20`).
    :param class_hash: class_hash of the contract to be deployed.
    :param calldata: Dict with constructor arguments (can be empty).
    :returns: Instance of the deployed contract.
    """
    contract_sierra = load_contract(contract_name)["sierra"]

    abi = create_sierra_compiled_contract(compiled_contract=contract_sierra).parsed_abi

    deployer = Deployer()
    deploy_call, address = deployer.create_contract_deployment(
        class_hash=class_hash,
        abi=abi,
        calldata=calldata,
        cairo_version=1,
    )
    res = await account.execute_v1(calls=deploy_call, max_fee=MAX_FEE)
    await account.client.wait_for_tx(res.transaction_hash)

    return Contract(address, abi, provider=account, cairo_version=1)


@pytest.fixture(scope="package")
def eth_fee_contract(account: BaseAccount, fee_contract_abi) -> Contract:
    """
    Returns an instance of the ETH fee contract. It is used to transfer tokens.
    """

    return Contract(
        address=FEE_CONTRACT_ADDRESS,
        abi=fee_contract_abi,
        provider=account,
        cairo_version=0,
    )


@pytest.fixture(scope="package")
def strk_fee_contract(account: BaseAccount, fee_contract_abi) -> Contract:
    """
    Returns an instance of the STRK fee contract. It is used to transfer tokens.
    """

    return Contract(
        address=STRK_FEE_CONTRACT_ADDRESS,
        abi=fee_contract_abi,
        provider=account,
        cairo_version=0,
    )


@pytest.fixture(scope="package")
def fee_contract_abi():
    return [
        {
            "inputs": [
                {"name": "recipient", "type": "felt"},
                {"name": "amount", "type": "Uint256"},
            ],
            "name": "transfer",
            "outputs": [{"name": "success", "type": "felt"}],
            "type": "function",
        },
        {
            "members": [
                {"name": "low", "offset": 0, "type": "felt"},
                {"name": "high", "offset": 1, "type": "felt"},
            ],
            "name": "Uint256",
            "size": 2,
            "type": "struct",
        },
    ]


async def declare_account(
    account: BaseAccount, compiled_contract: str, compiled_class_hash: int
) -> int:
    """
    Declares a specified account.
    """

    declare_tx = await account.sign_declare_v2(
        compiled_contract,
        compiled_class_hash,
        max_fee=MAX_FEE,
    )
    resp = await account.client.declare(transaction=declare_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    return resp.class_hash


async def declare_cairo1_account(
    account: BaseAccount,
    compiled_account_contract: str,
    compiled_account_contract_casm: str,
) -> int:
    """
    Declares a specified Cairo1 account.
    """

    casm_class = create_casm_class(compiled_account_contract_casm)
    casm_class_hash = compute_casm_class_hash(casm_class)
    declare_v2_transaction = await account.sign_declare_v2(
        compiled_contract=compiled_account_contract,
        compiled_class_hash=casm_class_hash,
        max_fee=MAX_FEE,
    )
    resp = await account.client.declare(transaction=declare_v2_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)
    return resp.class_hash


@pytest_asyncio.fixture(scope="package")
async def account_with_validate_deploy_class_hash(
    pre_deployed_account_with_validate_deploy: BaseAccount,
) -> int:
    contract = load_contract("Account")
    casm_class_hash = compute_casm_class_hash(create_casm_class(contract["casm"]))

    return await declare_account(
        pre_deployed_account_with_validate_deploy, contract["sierra"], casm_class_hash
    )


@pytest_asyncio.fixture(scope="package")
async def argent_cairo1_account_class_hash(
    account: BaseAccount,
) -> int:
    # Use precompiled argent account contracts
    # we don't have the source code for this contract
    compiled_contract = read_contract(
        "argent_account.json", directory=PRECOMPILED_CONTRACTS_DIR
    )
    compiled_contract_casm = read_contract(
        "argent_account.casm", directory=PRECOMPILED_CONTRACTS_DIR
    )
    return await declare_cairo1_account(
        account=account,
        compiled_account_contract=compiled_contract,
        compiled_account_contract_casm=compiled_contract_casm,
    )
