# pylint: disable=redefined-outer-name
import json
from typing import Any, Dict, List, Optional, Tuple

import pytest
import pytest_asyncio

from starknet_py.common import (
    create_casm_class,
    create_compiled_contract,
    create_sierra_compiled_contract,
)
from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import (
    CONTRACTS_COMPILED_V1_DIR,
    CONTRACTS_DIR,
    MAX_FEE,
)
from starknet_py.tests.e2e.fixtures.misc import read_contract


@pytest.fixture(scope="package")
def map_source_code() -> str:
    """
    Returns source code of the map contract.
    """
    return read_contract("map.cairo", directory=CONTRACTS_DIR)


@pytest.fixture(scope="package")
def map_compiled_contract() -> str:
    """
    Returns compiled map contract.
    """
    return read_contract("map_compiled.json")


@pytest.fixture(scope="package")
def sierra_minimal_compiled_contract_and_class_hash() -> Tuple[str, int]:
    """
    Returns minimal contract compiled to sierra and its compiled class hash.
    """
    compiled_contract = read_contract(
        "minimal_contract_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    compiled_contract_casm = read_contract(
        "minimal_contract_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
    )
    return (
        compiled_contract,
        compute_casm_class_hash(create_casm_class(compiled_contract_casm)),
    )


@pytest.fixture(scope="package")
def simple_storage_with_event_compiled_contract() -> str:
    """
    Returns compiled simple storage contract that emits an event.
    """
    return read_contract("simple_storage_with_event_compiled.json")


@pytest.fixture(scope="package")
def erc20_compiled_contract() -> str:
    """
    Returns compiled erc20 contract.
    """
    return read_contract("erc20_compiled.json")


@pytest.fixture(scope="package")
def constructor_with_arguments_compiled_contract() -> str:
    """
    Returns compiled constructor_with_arguments contract.
    """
    return read_contract("constructor_with_arguments_compiled.json")


@pytest.fixture(scope="package")
def constructor_without_arguments_compiled_contract() -> str:
    """
    Returns compiled constructor_without_arguments contract.
    """
    return read_contract("constructor_without_arguments_compiled.json")


async def deploy_contract(account: BaseAccount, class_hash: int, abi: List) -> Contract:
    """
    Deploys a contract and returns its instance.
    """
    deployment_result = await Contract.deploy_contract(
        account=account, class_hash=class_hash, abi=abi, max_fee=MAX_FEE
    )
    deployment_result = await deployment_result.wait_for_acceptance()
    return deployment_result.deployed_contract


async def deploy_v1_contract(
    account: BaseAccount,
    contract_file_name: str,
    class_hash: int,
    calldata: Optional[Dict[str, Any]] = None,
) -> Contract:
    """
    Declares and deploys Cairo1.0 contract.

    :param account: An account which will be used to invoke the Contract.
    :param contract_file_name: Name of the file with code (e.g. `erc20` if filename is `erc20.cairo`).
    :param class_hash: class_hash of the contract to be deployed.
    :param calldata: Dict with constructor arguments (can be empty).
    :returns: Instance of the deployed contract.
    """
    contract_sierra = read_contract(
        contract_file_name + "_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    sierra_compiled_contract = create_sierra_compiled_contract(
        compiled_contract=contract_sierra
    )
    abi = json.loads(sierra_compiled_contract.abi)

    deployer = Deployer()
    deploy_call, address = deployer.create_contract_deployment(
        class_hash=class_hash,
        abi=abi,
        calldata=calldata,
        cairo_version=1,
    )
    res = await account.execute(calls=deploy_call, max_fee=MAX_FEE)
    await account.client.wait_for_tx(res.transaction_hash)

    return Contract(address, abi, provider=account, cairo_version=1)


@pytest_asyncio.fixture(scope="package")
async def deployed_balance_contract(
    gateway_account: BaseAccount,
    balance_contract: str,
) -> Contract:
    """
    Declares, deploys a new balance contract and returns its instance.
    """
    declare_result = await Contract.declare(
        account=gateway_account,
        compiled_contract=balance_contract,
        max_fee=int(1e16),
    )
    await declare_result.wait_for_acceptance()

    deploy_result = await declare_result.deploy(max_fee=int(1e16))
    await deploy_result.wait_for_acceptance()

    return deploy_result.deployed_contract


@pytest_asyncio.fixture(scope="package")
async def map_contract(
    gateway_account: BaseAccount,
    map_compiled_contract: str,
    map_class_hash: int,
) -> Contract:
    """
    Deploys map contract and returns its instance.
    """
    abi = create_compiled_contract(compiled_contract=map_compiled_contract).abi
    return await deploy_contract(gateway_account, map_class_hash, abi)


@pytest_asyncio.fixture(scope="function")
async def simple_storage_with_event_contract(
    gateway_account: BaseAccount,
    simple_storage_with_event_compiled_contract: str,
    simple_storage_with_event_class_hash: int,
) -> Contract:
    """
    Deploys storage contract with an events and returns its instance.
    """
    abi = create_compiled_contract(
        compiled_contract=simple_storage_with_event_compiled_contract
    ).abi
    return await deploy_contract(
        gateway_account, simple_storage_with_event_class_hash, abi
    )


@pytest_asyncio.fixture(name="erc20_contract", scope="package")
async def deploy_erc20_contract(
    gateway_account: BaseAccount,
    erc20_compiled_contract: str,
    erc20_class_hash: int,
) -> Contract:
    """
    Deploys erc20 contract and returns its instance.
    """
    abi = create_compiled_contract(compiled_contract=erc20_compiled_contract).abi
    return await deploy_contract(gateway_account, erc20_class_hash, abi)


@pytest.fixture(scope="package")
def fee_contract(gateway_account: BaseAccount) -> Contract:
    """
    Returns an instance of the fee contract. It is used to transfer tokens.
    """
    abi = [
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

    return Contract(
        address=FEE_CONTRACT_ADDRESS,
        abi=abi,
        provider=gateway_account,
    )


@pytest.fixture(name="balance_contract")
def fixture_balance_contract() -> str:
    """
    Returns compiled code of the balance.cairo contract.
    """
    return read_contract("balance_compiled.json")


async def declare_account(account: BaseAccount, compiled_account_contract: str) -> int:
    """
    Declares a specified account.
    """

    declare_tx = await account.sign_declare_transaction(
        compiled_contract=compiled_account_contract,
        max_fee=MAX_FEE,
    )
    resp = await account.client.declare(transaction=declare_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    return resp.class_hash


@pytest_asyncio.fixture(scope="package")
async def account_with_validate_deploy_class_hash(
    pre_deployed_account_with_validate_deploy: BaseAccount,
) -> int:
    compiled_contract = read_contract("account_with_validate_deploy_compiled.json")
    return await declare_account(
        pre_deployed_account_with_validate_deploy, compiled_contract
    )


@pytest_asyncio.fixture(scope="package")
async def map_class_hash(
    gateway_account: BaseAccount, map_compiled_contract: str
) -> int:
    """
    Returns class_hash of the map.cairo.
    """
    declare = await gateway_account.sign_declare_transaction(
        compiled_contract=map_compiled_contract,
        max_fee=int(1e16),
    )
    res = await gateway_account.client.declare(declare)
    await gateway_account.client.wait_for_tx(res.transaction_hash)
    return res.class_hash


@pytest_asyncio.fixture(scope="package")
async def simple_storage_with_event_class_hash(
    gateway_account: BaseAccount, simple_storage_with_event_compiled_contract: str
):
    """
    Returns class_hash of the simple_storage_with_event.cairo
    """
    declare = await gateway_account.sign_declare_transaction(
        compiled_contract=simple_storage_with_event_compiled_contract,
        max_fee=int(1e16),
    )
    res = await gateway_account.client.declare(declare)
    await gateway_account.client.wait_for_tx(res.transaction_hash)
    return res.class_hash


@pytest_asyncio.fixture(scope="package")
async def erc20_class_hash(
    gateway_account: BaseAccount, erc20_compiled_contract: str
) -> int:
    """
    Returns class_hash of the erc20.cairo.
    """
    declare = await gateway_account.sign_declare_transaction(
        compiled_contract=erc20_compiled_contract,
        max_fee=int(1e16),
    )
    res = await gateway_account.client.declare(declare)
    await gateway_account.client.wait_for_tx(res.transaction_hash)
    return res.class_hash


constructor_with_arguments_source = (
    CONTRACTS_DIR / "constructor_with_arguments.cairo"
).read_text("utf-8")


@pytest.fixture(scope="package")
def constructor_with_arguments_abi() -> List:
    """
    Returns an abi of the constructor_with_arguments.cairo.
    """
    compiled_contract = create_compiled_contract(
        compiled_contract=read_contract("constructor_with_arguments_compiled.json")
    )
    assert compiled_contract.abi is not None
    return compiled_contract.abi


@pytest.fixture(scope="package")
def constructor_with_arguments_compiled() -> str:
    """
    Returns a compiled constructor_with_arguments.cairo.
    """
    return read_contract("constructor_with_arguments_compiled.json")


@pytest_asyncio.fixture(scope="package")
async def constructor_with_arguments_class_hash(
    gateway_account: BaseAccount, constructor_with_arguments_compiled
) -> int:
    """
    Returns a class_hash of the constructor_with_arguments.cairo.
    """
    declare = await gateway_account.sign_declare_transaction(
        compiled_contract=constructor_with_arguments_compiled,
        max_fee=int(1e16),
    )
    res = await gateway_account.client.declare(declare)
    await gateway_account.client.wait_for_tx(res.transaction_hash)
    return res.class_hash
