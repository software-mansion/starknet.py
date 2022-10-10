from pathlib import Path

import pytest_asyncio

from starknet_py.net import AccountClient
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.tests.e2e.conftest import contracts_dir, MAX_FEE


@pytest_asyncio.fixture
async def deploy_account_transaction(
    new_gateway_account_client: AccountClient,
) -> DeployAccount:
    account_client = new_gateway_account_client

    compiled_contract = Path(
        contracts_dir / "contract_with_validate_deploy.cairo"
    ).read_text("utf-8")
    declare_tx = await account_client.sign_declare_transaction(
        compilation_source=compiled_contract, max_fee=MAX_FEE
    )
    declare_result = await account_client.declare(declare_tx)
    await account_client.wait_for_tx(declare_result.transaction_hash)

    return await new_gateway_account_client.sign_deploy_account_transaction(
        class_hash=declare_result.class_hash,
        contract_address_salt=10,
        constructor_calldata=[],
        max_fee=10000000000,
    )
