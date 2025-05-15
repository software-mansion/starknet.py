# pylint: disable=redefined-outer-name
from typing import Any, Dict, List, Optional, Tuple

import pytest
import pytest_asyncio

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.common import create_casm_class, create_sierra_compiled_contract
from starknet_py.contract import Contract
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.models import DeclareV3
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import MAX_RESOURCE_BOUNDS
from starknet_py.tests.e2e.fixtures.misc import ContractVersion, load_contract


async def declare_contract(
    account: BaseAccount, compiled_contract: str, compiled_contract_casm: str
) -> Tuple[int, int]:
    casm_class_hash = compute_casm_class_hash(create_casm_class(compiled_contract_casm))

    declare_tx = await account.sign_declare_v3(
        compiled_contract=compiled_contract,
        compiled_class_hash=casm_class_hash,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    assert declare_tx.version == 3

    resp = await account.client.declare(declare_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    return resp.class_hash, resp.transaction_hash


@pytest_asyncio.fixture(scope="package")
async def erc20_class_hash(account: BaseAccount) -> int:
    contract = load_contract("ERC20")
    class_hash, _ = await declare_contract(
        account, contract["sierra"], contract["casm"]
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def constructor_with_arguments_class_hash(account: BaseAccount) -> int:
    contract = load_contract("ConstructorWithArguments")
    class_hash, _ = await declare_contract(
        account, contract["sierra"], contract["casm"]
    )
    return class_hash


@pytest.fixture(scope="package")
def constructor_with_arguments_abi() -> List:
    """
    Returns an abi of the constructor_with_arguments.cairo.
    """
    compiled_contract = create_sierra_compiled_contract(
        compiled_contract=load_contract("ConstructorWithArguments")["sierra"]
    )
    assert compiled_contract.parsed_abi is not None
    return compiled_contract.parsed_abi


@pytest_asyncio.fixture(scope="package")
async def declare_v3_hello_starknet(account: BaseAccount) -> DeclareV3:
    contract = load_contract("HelloStarknet")
    casm_class_hash = compute_casm_class_hash(create_casm_class(contract["casm"]))

    declare_tx = await account.sign_declare_v3(
        contract["sierra"], casm_class_hash, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    return declare_tx


@pytest_asyncio.fixture(scope="package")
async def hello_starknet_class_hash_tx_hash(
    account: BaseAccount, declare_v3_hello_starknet: DeclareV3
) -> Tuple[int, int]:
    resp = await account.client.declare(declare_v3_hello_starknet)
    await account.client.wait_for_tx(resp.transaction_hash)

    return resp.class_hash, resp.transaction_hash


@pytest_asyncio.fixture(scope="package")
async def hello_starknet_abi() -> List:
    contract = load_contract("HelloStarknet")
    compiled_contract = create_sierra_compiled_contract(
        compiled_contract=contract["sierra"]
    )
    assert compiled_contract.parsed_abi is not None
    return compiled_contract.parsed_abi


@pytest.fixture(scope="package")
def hello_starknet_class_hash(hello_starknet_class_hash_tx_hash) -> int:
    class_hash, _ = hello_starknet_class_hash_tx_hash
    return class_hash


@pytest.fixture(scope="package")
def hello_starknet_tx_hash(hello_starknet_class_hash_tx_hash) -> int:
    _, tx_hash = hello_starknet_class_hash_tx_hash
    return tx_hash


@pytest_asyncio.fixture(scope="package")
async def minimal_contract_class_hash(account: BaseAccount) -> int:
    contract = load_contract("MinimalContract")
    class_hash, _ = await declare_contract(
        account,
        contract["sierra"],
        contract["casm"],
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def test_enum_class_hash(account: BaseAccount) -> int:
    contract = load_contract("TestEnum")
    class_hash, _ = await declare_contract(
        account,
        contract["sierra"],
        contract["casm"],
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def test_option_class_hash(account: BaseAccount) -> int:
    contract = load_contract("TestOption")
    class_hash, _ = await declare_contract(
        account,
        contract["sierra"],
        contract["casm"],
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def token_bridge_class_hash(account: BaseAccount) -> int:
    contract = load_contract("TokenBridge")
    class_hash, _ = await declare_contract(
        account,
        contract["sierra"],
        contract["casm"],
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def erc20_contract(account, erc20_class_hash):
    calldata = {
        "name_": encode_shortstring("erc20_basic"),
        "symbol_": encode_shortstring("ERC20B"),
        "decimals_": 10,
        "initial_supply": 200,
        "recipient": account.address,
    }
    return await deploy_v3_contract(
        account=account,
        contract_name="ERC20",
        class_hash=erc20_class_hash,
        calldata=calldata,
    )


@pytest_asyncio.fixture(scope="package")
async def hello_starknet_contract(account: BaseAccount, hello_starknet_class_hash):
    return await deploy_v3_contract(
        account=account,
        contract_name="HelloStarknet",
        class_hash=hello_starknet_class_hash,
    )


@pytest_asyncio.fixture(scope="package", name="string_contract_class_hash")
async def declare_string_contract(account: BaseAccount) -> int:
    contract = load_contract("MyString", version=ContractVersion.V2)
    class_hash, _ = await declare_contract(
        account, contract["sierra"], contract["casm"]
    )
    return class_hash


@pytest_asyncio.fixture(scope="package", name="string_contract")
async def deploy_string_contract(
    account: BaseAccount, string_contract_class_hash
) -> Contract:
    return await deploy_v3_contract(
        account=account,
        contract_name="MyString",
        class_hash=string_contract_class_hash,
    )


@pytest_asyncio.fixture(scope="package")
async def map_class_hash(account: BaseAccount) -> int:
    contract = load_contract("Map")
    class_hash, _ = await declare_contract(
        account,
        contract["sierra"],
        contract["casm"],
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def map_contract(account: BaseAccount, map_class_hash) -> Contract:
    return await deploy_v3_contract(
        account=account,
        contract_name="Map",
        class_hash=map_class_hash,
    )


@pytest_asyncio.fixture(scope="package")
async def map_abi() -> List:
    contract = load_contract("Map")
    compiled_contract = create_sierra_compiled_contract(
        compiled_contract=contract["sierra"]
    )
    assert compiled_contract.parsed_abi is not None
    return compiled_contract.parsed_abi


@pytest.fixture(scope="package")
def map_compiled_contract_and_class_hash() -> Tuple[str, int]:
    contract = load_contract("Map")

    return (
        contract["sierra"],
        compute_casm_class_hash(create_casm_class(contract["casm"])),
    )


@pytest.fixture(scope="package")
def map_compiled_contract_and_class_hash_copy_1() -> Tuple[str, int]:
    contract = load_contract("MapCopy1")

    return (
        contract["sierra"],
        compute_casm_class_hash(create_casm_class(contract["casm"])),
    )


@pytest.fixture(scope="package")
def map_compiled_contract_and_class_hash_copy_2() -> Tuple[str, int]:
    contract = load_contract("MapCopy2")

    return (
        contract["sierra"],
        compute_casm_class_hash(create_casm_class(contract["casm"])),
    )


@pytest.fixture(scope="package")
def map_compiled_contract_casm() -> str:
    contract = load_contract("Map")

    return contract["casm"]


@pytest_asyncio.fixture(scope="package")
async def simple_storage_with_event_class_hash(account: BaseAccount) -> int:
    contract = load_contract("SimpleStorageWithEvent")
    class_hash, _ = await declare_contract(
        account, contract["sierra"], contract["casm"]
    )
    return class_hash


@pytest_asyncio.fixture(scope="function")
async def simple_storage_with_event_contract(
    account: BaseAccount,
    simple_storage_with_event_class_hash: int,
) -> Contract:
    return await deploy_v3_contract(
        account=account,
        contract_name="SimpleStorageWithEvent",
        class_hash=simple_storage_with_event_class_hash,
    )


@pytest.fixture(scope="package")
def sierra_minimal_compiled_contract_and_class_hash() -> Tuple[str, int]:
    """
    Returns minimal contract compiled to sierra and its compiled class hash.
    """
    contract = load_contract("MinimalContract")

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


async def declare_account(
    account: BaseAccount, compiled_contract: str, compiled_class_hash: int
) -> int:
    """
    Declares a specified account.
    """

    declare_tx = await account.sign_declare_v3(
        compiled_contract,
        compiled_class_hash,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    resp = await account.client.declare(transaction=declare_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    return resp.class_hash


async def account_declare_class_hash(
    account: BaseAccount,
    compiled_account_contract: str,
    compiled_account_contract_casm: str,
) -> int:
    """
    Declares a specified Cairo1 account.
    """

    casm_class = create_casm_class(compiled_account_contract_casm)
    casm_class_hash = compute_casm_class_hash(casm_class)
    declare_v3_transaction = await account.sign_declare_v3(
        compiled_contract=compiled_account_contract,
        compiled_class_hash=casm_class_hash,
        resource_bounds=MAX_RESOURCE_BOUNDS,
    )
    resp = await account.client.declare(transaction=declare_v3_transaction)
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


async def deploy_v3_contract(
    account: BaseAccount,
    contract_name: str,
    class_hash: int,
    calldata: Optional[Dict[str, Any]] = None,
) -> Contract:
    """
    Deploys Cairo1 contract.

    :param account: An account which will be used to deploy the Contract.
    :param contract_name: Name of the contract from project mocks (e.g. `ERC20`).
    :param class_hash: class_hash of the contract to be deployed.
    :param calldata: Dict with constructor arguments (can be empty).
    :returns: Instance of the deployed contract.
    """
    contract_sierra = load_contract(contract_name)["sierra"]

    abi = create_sierra_compiled_contract(contract_sierra).parsed_abi

    deployer = Deployer()
    deploy_call, address = deployer.create_contract_deployment(
        class_hash=class_hash,
        abi=abi,
        calldata=calldata,
    )
    res = await account.execute_v3(
        calls=deploy_call, resource_bounds=MAX_RESOURCE_BOUNDS
    )
    await account.client.wait_for_tx(res.transaction_hash)

    return Contract(address, abi, provider=account)
