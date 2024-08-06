# pylint: disable=redefined-outer-name
from typing import List, Tuple

import pytest
import pytest_asyncio

from starknet_py.cairo.felt import encode_shortstring
from starknet_py.common import create_casm_class, create_sierra_compiled_contract
from starknet_py.contract import Contract
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.models import DeclareV2
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE
from starknet_py.tests.e2e.fixtures.contracts import deploy_v1_contract
from starknet_py.tests.e2e.fixtures.misc import ContractVersion, load_contract


async def declare_cairo1_contract(
    account: BaseAccount, compiled_contract: str, compiled_contract_casm: str
) -> Tuple[int, int]:
    casm_class_hash = compute_casm_class_hash(create_casm_class(compiled_contract_casm))

    declare_tx = await account.sign_declare_v2(
        compiled_contract=compiled_contract,
        compiled_class_hash=casm_class_hash,
        max_fee=MAX_FEE,
    )
    assert declare_tx.version == 2

    resp = await account.client.declare(declare_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    return resp.class_hash, resp.transaction_hash


@pytest_asyncio.fixture(scope="package")
async def cairo1_erc20_class_hash(account: BaseAccount) -> int:
    contract = load_contract("ERC20")
    class_hash, _ = await declare_cairo1_contract(
        account, contract["sierra"], contract["casm"]
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def constructor_with_arguments_class_hash(account: BaseAccount) -> int:
    contract = load_contract("ConstructorWithArguments")
    class_hash, _ = await declare_cairo1_contract(
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
async def declare_v2_hello_starknet(account: BaseAccount) -> DeclareV2:
    contract = load_contract("HelloStarknet")
    casm_class_hash = compute_casm_class_hash(create_casm_class(contract["casm"]))

    declare_tx = await account.sign_declare_v2(
        contract["sierra"], casm_class_hash, max_fee=MAX_FEE
    )
    return declare_tx


@pytest_asyncio.fixture(scope="package")
async def cairo1_hello_starknet_class_hash_tx_hash(
    account: BaseAccount, declare_v2_hello_starknet: DeclareV2
) -> Tuple[int, int]:
    resp = await account.client.declare(declare_v2_hello_starknet)
    await account.client.wait_for_tx(resp.transaction_hash)

    return resp.class_hash, resp.transaction_hash


@pytest.fixture(scope="package")
def cairo1_hello_starknet_class_hash(
    cairo1_hello_starknet_class_hash_tx_hash: Tuple[int, int]
) -> int:
    class_hash, _ = cairo1_hello_starknet_class_hash_tx_hash
    return class_hash


@pytest.fixture(scope="package")
def cairo1_hello_starknet_tx_hash(
    cairo1_hello_starknet_class_hash_tx_hash: Tuple[int, int]
) -> int:
    _, tx_hash = cairo1_hello_starknet_class_hash_tx_hash
    return tx_hash


@pytest_asyncio.fixture(scope="package")
async def cairo1_minimal_contract_class_hash(account: BaseAccount) -> int:
    contract = load_contract(contract_name="MinimalContract")
    class_hash, _ = await declare_cairo1_contract(
        account,
        contract["sierra"],
        contract["casm"],
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def cairo1_test_enum_class_hash(account: BaseAccount) -> int:
    contract = load_contract(contract_name="TestEnum")
    class_hash, _ = await declare_cairo1_contract(
        account,
        contract["sierra"],
        contract["casm"],
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def cairo1_test_option_class_hash(account: BaseAccount) -> int:
    contract = load_contract(contract_name="TestOption")
    class_hash, _ = await declare_cairo1_contract(
        account,
        contract["sierra"],
        contract["casm"],
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def cairo1_token_bridge_class_hash(account: BaseAccount) -> int:
    contract = load_contract(contract_name="TokenBridge")
    class_hash, _ = await declare_cairo1_contract(
        account,
        contract["sierra"],
        contract["casm"],
    )
    return class_hash


@pytest_asyncio.fixture(scope="package", name="erc20_contract")
async def cairo1_erc20_deploy(account, cairo1_erc20_class_hash):
    calldata = {
        "name_": encode_shortstring("erc20_basic"),
        "symbol_": encode_shortstring("ERC20B"),
        "decimals_": 10,
        "initial_supply": 200,
        "recipient": account.address,
    }
    return await deploy_v1_contract(
        account=account,
        contract_name="ERC20",
        class_hash=cairo1_erc20_class_hash,
        calldata=calldata,
    )


@pytest_asyncio.fixture(scope="package", name="hello_starknet_contract")
async def cairo1_hello_starknet_deploy(
    account: BaseAccount, cairo1_hello_starknet_class_hash
):
    return await deploy_v1_contract(
        account=account,
        contract_name="HelloStarknet",
        class_hash=cairo1_hello_starknet_class_hash,
    )


@pytest_asyncio.fixture(scope="package", name="string_contract_class_hash")
async def declare_string_contract(account: BaseAccount) -> int:
    contract = load_contract("MyString", version=ContractVersion.V2)
    class_hash, _ = await declare_cairo1_contract(
        account, contract["sierra"], contract["casm"]
    )
    return class_hash


@pytest_asyncio.fixture(scope="package", name="string_contract")
async def deploy_string_contract(
    account: BaseAccount, string_contract_class_hash
) -> Contract:
    return await deploy_v1_contract(
        account=account,
        contract_name="MyString",
        class_hash=string_contract_class_hash,
    )


@pytest_asyncio.fixture(scope="package")
async def cairo1_map_contract_declare_hash(account: BaseAccount) -> int:
    contract = load_contract(contract_name="Map")
    class_hash, _ = await declare_cairo1_contract(
        account,
        contract["sierra"],
        contract["casm"],
    )
    return class_hash


@pytest_asyncio.fixture(scope="package", name="map_contract")
async def deploy_map_contract(
    account: BaseAccount, cairo1_map_contract_declare_hash
) -> Contract:
    return await deploy_v1_contract(
        account=account,
        contract_name="Map",
        class_hash=cairo1_map_contract_declare_hash,
    )


@pytest_asyncio.fixture(scope="package")
async def cairo1_map_contract_abi() -> List:
    contract = load_contract(contract_name="Map")
    compiled_contract = create_sierra_compiled_contract(
        compiled_contract=contract["sierra"]
    )
    assert compiled_contract.parsed_abi is not None
    return compiled_contract.parsed_abi
