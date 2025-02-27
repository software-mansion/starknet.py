import pytest_asyncio

from starknet_py.contract import Contract
from starknet_py.tests.e2e.fixtures.contracts_v1 import (
    declare_contract,
    deploy_v3_contract,
)
from starknet_py.tests.e2e.fixtures.misc import load_contract


@pytest_asyncio.fixture(scope="package", name="f_string_contract_class_hash")
async def declare_string_contract(account_forked_devnet) -> int:
    contract = load_contract("MyString")
    class_hash, _ = await declare_contract(
        account_forked_devnet, contract["sierra"], contract["casm"]
    )
    return class_hash


@pytest_asyncio.fixture(scope="package", name="f_string_contract")
async def deploy_string_contract(
    account_forked_devnet, f_string_contract_class_hash
) -> Contract:
    return await deploy_v3_contract(
        account=account_forked_devnet,
        contract_name="MyString",
        class_hash=f_string_contract_class_hash,
    )


@pytest_asyncio.fixture(scope="package", name="l1_l2_contract_class_hash")
async def declare_l1_l2_contract(account) -> int:
    contract = load_contract("l1_l2")
    class_hash, _ = await declare_contract(
        account, contract["sierra"], contract["casm"]
    )
    return class_hash


@pytest_asyncio.fixture(scope="package", name="l1_l2_contract")
async def deploy_l1_l2_contract(account, l1_l2_contract_class_hash) -> Contract:
    return await deploy_v3_contract(
        account=account,
        contract_name="l1_l2",
        class_hash=l1_l2_contract_class_hash,
    )
