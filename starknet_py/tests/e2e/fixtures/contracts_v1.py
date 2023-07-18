# pylint: disable=redefined-outer-name
import json
from typing import Any, Dict, Optional, Tuple

import pytest
import pytest_asyncio

from starknet_py.common import create_casm_class, create_sierra_compiled_contract
from starknet_py.contract import Contract
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.models import DeclareV2
from starknet_py.net.udc_deployer.deployer import Deployer
from starknet_py.tests.e2e.fixtures.constants import MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import read_contract


async def declare_cairo1_contract(
    account: BaseAccount, compiled_contract: str, compiled_contract_casm: str
) -> Tuple[int, int]:
    casm_class_hash = compute_casm_class_hash(create_casm_class(compiled_contract_casm))

    declare_tx = await account.sign_declare_v2_transaction(
        compiled_contract=compiled_contract,
        compiled_class_hash=casm_class_hash,
        max_fee=MAX_FEE,
    )
    assert declare_tx.version == 2

    resp = await account.client.declare(declare_tx)
    await account.client.wait_for_tx(resp.transaction_hash)

    return resp.class_hash, resp.transaction_hash


async def deploy_v1_contract(
    account: BaseAccount,
    contract_file_name: str,
    class_hash: int,
    calldata: Optional[Dict[str, Any]] = None,
) -> Contract:
    """
    Deploys Cairo1.0 contract.

    :param account: An account which will be used to deploy the Contract.
    :param contract_file_name: Name of the file with code (e.g. `erc20` if filename is `erc20.cairo`).
    :param class_hash: class_hash of the contract to be deployed.
    :param calldata: Dict with constructor arguments (can be empty).
    :returns: Instance of the deployed contract.
    """
    contract_sierra = read_contract(contract_file_name + "_compiled.json")
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


@pytest.fixture(scope="package")
def sierra_minimal_compiled_contract_and_class_hash() -> Tuple[str, int]:
    """
    Returns minimal contract compiled to sierra and its compiled class hash.
    """
    compiled_contract = read_contract("minimal_contract_compiled.json", v1_v2=True)
    compiled_contract_casm = read_contract("minimal_contract_compiled.casm", v1_v2=True)
    return (
        compiled_contract,
        compute_casm_class_hash(create_casm_class(compiled_contract_casm)),
    )


@pytest_asyncio.fixture(scope="package")
async def cairo1_erc20_class_hash(account: BaseAccount) -> int:
    class_hash, _ = await declare_cairo1_contract(
        account,
        read_contract("erc20_compiled.json", v1_v2=True),
        read_contract("erc20_compiled.casm", v1_v2=True),
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def declare_v2_hello_starknet(account: BaseAccount) -> DeclareV2:
    compiled_contract = read_contract("hello_starknet_compiled.json", v1_v2=True)
    compiled_contract_casm = read_contract("hello_starknet_compiled.casm", v1_v2=True)
    casm_class_hash = compute_casm_class_hash(create_casm_class(compiled_contract_casm))

    declare_tx = await account.sign_declare_v2_transaction(
        compiled_contract, casm_class_hash, max_fee=MAX_FEE
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
    class_hash, _ = await declare_cairo1_contract(
        account,
        read_contract("minimal_contract_compiled.json", v1_v2=True),
        read_contract("minimal_contract_compiled.casm", v1_v2=True),
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def cairo1_test_enum_class_hash(account: BaseAccount) -> int:
    class_hash, _ = await declare_cairo1_contract(
        account,
        read_contract("test_enum_compiled.json", v1_v2=True),
        read_contract("test_enum_compiled.casm", v1_v2=True),
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def cairo1_test_option_class_hash(account: BaseAccount) -> int:
    class_hash, _ = await declare_cairo1_contract(
        account,
        read_contract("test_option_compiled.json", v1_v2=True),
        read_contract("test_option_compiled.casm", v1_v2=True),
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def cairo1_token_bridge_class_hash(account: BaseAccount) -> int:
    class_hash, _ = await declare_cairo1_contract(
        account,
        read_contract("token_bridge_compiled.json", v1_v2=True),
        read_contract("token_bridge_compiled.casm", v1_v2=True),
    )
    return class_hash
