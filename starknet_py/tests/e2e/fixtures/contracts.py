# pylint: disable=redefined-outer-name
from typing import List

import pytest
import pytest_asyncio

from starknet_py.common import create_compiled_contract
from starknet_py.constants import FEE_CONTRACT_ADDRESS
from starknet_py.contract import Contract
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.account.compiled_account_contract import COMPILED_ACCOUNT_CONTRACT
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_DIR, MAX_FEE
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
def base_compiled_contract() -> str:
    """
    Returns compiled base contract.
    """
    return read_contract("base_compiled.json")


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
async def account_without_validate_deploy_class_hash(
    pre_deployed_account_with_validate_deploy: BaseAccount,
) -> int:
    return await declare_account(
        pre_deployed_account_with_validate_deploy, COMPILED_ACCOUNT_CONTRACT
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
        compilation_source=constructor_with_arguments_source
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
