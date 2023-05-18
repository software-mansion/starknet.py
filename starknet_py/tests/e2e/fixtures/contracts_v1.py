# pylint: disable=redefined-outer-name
from typing import Tuple

import pytest
import pytest_asyncio

from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.account.base_account import BaseAccount
from starknet_py.net.models import DeclareV2
from starknet_py.tests.e2e.fixtures.constants import CONTRACTS_COMPILED_V1_DIR, MAX_FEE
from starknet_py.tests.e2e.fixtures.misc import read_contract


async def declare_v1_contract(
    gateway_account: BaseAccount, compiled_contract: str, compiled_contract_casm: str
) -> Tuple[int, int]:
    # TODO (#1023): replace with account after RPC 0.3.0
    casm_class_hash = compute_casm_class_hash(create_casm_class(compiled_contract_casm))

    declare_tx = await gateway_account.sign_declare_v2_transaction(
        compiled_contract, casm_class_hash, max_fee=MAX_FEE
    )
    resp = await gateway_account.client.declare(declare_tx)
    await gateway_account.client.wait_for_tx(resp.transaction_hash)

    return resp.class_hash, resp.transaction_hash


@pytest_asyncio.fixture(scope="package")
async def v1_account_class_hash(gateway_account: BaseAccount) -> int:
    # TODO (#1023): replace with account after RPC 0.3.0
    class_hash, _ = await declare_v1_contract(
        gateway_account,
        read_contract(
            "gateway_account_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
        ),
        read_contract(
            "gateway_account_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
        ),
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def v1_erc20_class_hash(gateway_account: BaseAccount) -> int:
    # TODO (#1023): replace with account after RPC 0.3.0
    class_hash, _ = await declare_v1_contract(
        gateway_account,
        read_contract("erc20_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR),
        read_contract("erc20_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR),
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def declare_v2_hello_starknet(gateway_account: BaseAccount) -> DeclareV2:
    # TODO (#1023): replace with account after RPC 0.3.0
    compiled_contract = read_contract(
        "hello_starknet_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
    )
    compiled_contract_casm = read_contract(
        "hello_starknet_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
    )
    casm_class_hash = compute_casm_class_hash(create_casm_class(compiled_contract_casm))

    declare_tx = await gateway_account.sign_declare_v2_transaction(
        compiled_contract, casm_class_hash, max_fee=MAX_FEE
    )
    return declare_tx


@pytest_asyncio.fixture(scope="package")
async def v1_hello_starknet_class_hash_tx_hash(
    gateway_account: BaseAccount, declare_v2_hello_starknet: DeclareV2
) -> Tuple[int, int]:
    # TODO (#1023): replace with account after RPC 0.3.0
    resp = await gateway_account.client.declare(declare_v2_hello_starknet)
    await gateway_account.client.wait_for_tx(resp.transaction_hash)

    return resp.class_hash, resp.transaction_hash


@pytest.fixture(scope="package")
def v1_hello_starknet_class_hash(
    v1_hello_starknet_class_hash_tx_hash: Tuple[int, int]
) -> int:
    class_hash, _ = v1_hello_starknet_class_hash_tx_hash
    return class_hash


@pytest.fixture(scope="package")
def v1_hello_starknet_tx_hash(
    v1_hello_starknet_class_hash_tx_hash: Tuple[int, int]
) -> int:
    _, tx_hash = v1_hello_starknet_class_hash_tx_hash
    return tx_hash


@pytest_asyncio.fixture(scope="package")
async def v1_minimal_contract_class_hash(gateway_account: BaseAccount) -> int:
    # TODO (#1023): replace with account after RPC 0.3.0
    class_hash, _ = await declare_v1_contract(
        gateway_account,
        read_contract(
            "minimal_contract_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
        ),
        read_contract(
            "minimal_contract_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
        ),
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def v1_test_contract_class_hash(gateway_account: BaseAccount) -> int:
    # TODO (#1023): replace with account after RPC 0.3.0
    class_hash, _ = await declare_v1_contract(
        gateway_account,
        read_contract(
            "test_contract_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
        ),
        read_contract(
            "test_contract_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
        ),
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def v1_test_enum_class_hash(gateway_account: BaseAccount) -> int:
    # TODO (#1023): replace with account after RPC 0.3.0
    class_hash, _ = await declare_v1_contract(
        gateway_account,
        read_contract("test_enum_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR),
        read_contract("test_enum_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR),
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def v1_test_option_class_hash(gateway_account: BaseAccount) -> int:
    # TODO (#1023): replace with account after RPC 0.3.0
    class_hash, _ = await declare_v1_contract(
        gateway_account,
        read_contract("test_option_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR),
        read_contract("test_option_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR),
    )
    return class_hash


@pytest_asyncio.fixture(scope="package")
async def v1_token_bridge_class_hash(gateway_account: BaseAccount) -> int:
    # TODO (#1023): replace with account after RPC 0.3.0
    class_hash, _ = await declare_v1_contract(
        gateway_account,
        read_contract(
            "token_bridge_compiled.json", directory=CONTRACTS_COMPILED_V1_DIR
        ),
        read_contract(
            "token_bridge_compiled.casm", directory=CONTRACTS_COMPILED_V1_DIR
        ),
    )
    return class_hash
